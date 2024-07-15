import os
import time
from io import BytesIO

import numpy as np
import requests
import torch
from PIL import Image
import replicate

import folder_paths

API_KEY = os.environ.get("REPLICATE_API_TOKEN")
video_extensions = ["mp4", "mov", "avi", "mkv", "webm"]
# Check for API key in file as a backup, not recommended
try:
    if not API_KEY:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "replicate_api_key.txt"), "r") as f:
            API_KEY = f.read().strip()
        # Validate the key is not empty
        if API_KEY.strip() == "":
            raise Exception(
                f"API Key is required to use Replicate API. \nPlease set the REPLICATE_API_TOKEN environment variable to your API key or place in {dir_path}/replicate_api_key.txt.")

except Exception as e:
    print(
        f"\n\n***API Key is required to use Replicate API. Please set the REPLICATE_API_TOKEN environment variable to your API key or place in {dir_path}/replicate_api_key.txt.***\n\n")

ROOT_API = "https://api.replicate.com/v1/predictions"


class PreviewVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "video": ("VIDEO",),
        }}

    CATEGORY = "LightSketch"
    DESCRIPTION = "hello world!"

    RETURN_TYPES = ()

    OUTPUT_NODE = True

    FUNCTION = "load_video"

    def load_video(self, video):
        print('Loading video......')
        print(video)
        video_name = os.path.basename(video)
        video_path_name = os.path.basename(os.path.dirname(video))
        return {"ui": {"video": [video_name, video_path_name]}}

class LightSketchLivePortrait:
    API_ENDPOINT = ""
    POLL_ENDPOINT = ""
    ACCEPT = "video/*"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        vid_files = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_parts = f.split('.')
                if len(file_parts) > 1 and (file_parts[-1] in video_extensions):
                    vid_files.append(f)
        return {
            "required": {
                "face_image": ("IMAGE", ),
                "video": (sorted(vid_files),),
            },
            "optional": {
                "live_portrait_dsize": ("INT", {"default": 512}),
                "live_portrait_scale": ("FLOAT", {"default": 2.3}),
                "video_frame_load_cap": ("INT", {"default": 128}),
                "live_portrait_lip_zero": ("BOOLEAN", {"default": True}),
                "live_portrait_relative": ("BOOLEAN", {"default": True}),
                "live_portrait_vx_ratio": ("FLOAT", {"default": 0}),
                "live_portrait_vy_ratio": ("FLOAT", {"default": -0.12}),
                "live_portrait_stitching": ("BOOLEAN", {"default": True}),
                "video_select_every_n_frames": ("INT", {"default": 1}),
                "live_portrait_eye_retargeting": ("BOOLEAN", {"default": False}),
                "live_portrait_lip_retargeting": ("BOOLEAN", {"default": False}),
                "live_portrait_lip_retargeting_multiplier": ("FLOAT", {"default": 1}),
                "live_portrait_eyes_retargeting_multiplier": ("FLOAT", {"default": 1}),
                "api_key_override": ("STRING", {"multiline": False}),
            }
        }

    RETURN_TYPES = ("VIDEO",)
    RETURN_NAMES = ("video",)
    FUNCTION = "call"
    CATEGORY = "LightSketch"

    def call(self, *args, **kwargs):
        # Check for required arguments
        face_image = kwargs.get('face_image')
        video = kwargs.get('video')

        if face_image is None or video is None:
            raise ValueError("Both face_image and video are required.")

        kwargs['comfyui'] = True

        api_key = os.environ.get("REPLICATE_API_TOKEN")

        if kwargs.get("api_key_override"):
            api_key = kwargs.get("api_key_override")


        if api_key is None:
            raise ValueError("API Key is required to use Replicate API. \nPlease set the REPLICATE_API_TOKEN environment variable to your API key or place in replicate_api_key.txt.")

        replicate_client = replicate.Client(api_token=api_key)

        # Convert face_image to bytes given that it is a tensor
        # Assuming face_image is a tensor or ndarray
        face_image = face_image.numpy()  # Convert to numpy array if it's a tensor
        face_image = (face_image * 255).astype(np.uint8)

        # Check the shape and squeeze unnecessary dimensions
        face_image = np.squeeze(face_image)

        # Now face_image should be of shape (height, width, channels)
        face_image = Image.fromarray(face_image)
        buffered = BytesIO()
        face_image.save(buffered, format="PNG")
        buffered.seek(0)

        output = replicate_client.run("lightsketch-ai/live-portrait:f4ebc0d95243b1cd5d904f63bf199d4bb587ce676ccfda59e7b5d58be3d08b2b",
           input={
            "face_image": buffered,
            "driving_video": open(folder_paths.get_input_directory() + '/' + kwargs.get('video'), 'rb'),
            "live_portrait_dsize": kwargs.get('live_portrait_dsize', 512),
            "live_portrait_scale": kwargs.get('live_portrait_scale', 2.3),
            "video_frame_load_cap": kwargs.get('video_frame_load_cap', 128),
            "live_portrait_lip_zero": kwargs.get('live_portrait_lip_zero', True),
            "live_portrait_relative": kwargs.get('live_portrait_relative', True),
            "live_portrait_vx_ratio": kwargs.get('live_portrait_vx_ratio', 0),
            "live_portrait_vy_ratio": kwargs.get('live_portrait_vy_ratio', -0.12),
            "live_portrait_stitching": kwargs.get('live_portrait_stitching', True),
            "video_select_every_n_frames": kwargs.get('video_select_every_n_frames', 1),
            "live_portrait_eye_retargeting": kwargs.get('live_portrait_eye_retargeting', False),
            "live_portrait_lip_retargeting": kwargs.get('live_portrait_lip_retargeting', False),
            "live_portrait_lip_retargeting_multiplier": kwargs.get('live_portrait_lip_retargeting_multiplier', 1),
            "live_portrait_eyes_retargeting_multiplier": kwargs.get('live_portrait_eyes_retargeting_multiplier', 1)
            }
        )
        print(output)

        # Given that output[0] is a url, save the video to the output_video folder (create that folder if doesn't exist)
        output_video_dir = 'output'
        if not os.path.exists(output_video_dir):
            os.makedirs(output_video_dir)

        # Create a name for the video based on the current time
        curr_time = time.time()

        vid_name = f'output_{curr_time}.mp4'

        output_video_path = os.path.join(output_video_dir, vid_name)
        with open(output_video_path, 'wb') as f:
            f.write(requests.get(output[0]).content)

        return (output_video_path,)

    def _return_image(self, response):
        result_image = Image.open(BytesIO(response.content))
        result_image = result_image.convert("RGBA")
        result_image = np.array(result_image).astype(np.float32) / 255.0
        result_image = torch.from_numpy(result_image)[None,]
        return (result_image,)

    def _return_video(self, response):
        result_video = response.content
        return (result_video,)

    def _get_files(self, buffered, **kwargs):
        return {
            "image": buffered.getvalue()
        }

    def _get_data(self, **kwargs):
        return {
            "version": "f4ebc0d95243b1cd5d904f63bf199d4bb587ce676ccfda59e7b5d58be3d08b2b",
            "input": {
                "face_image": kwargs.get('face_image'),
                "video": kwargs.get('video'),
                "live_portrait_dsize": kwargs.get('live_portrait_dsize', 512),
                "live_portrait_scale": kwargs.get('live_portrait_scale', 2.3),
                "video_frame_load_cap": kwargs.get('video_frame_load_cap', 128),
                "live_portrait_lip_zero": kwargs.get('live_portrait_lip_zero', True),
                "live_portrait_relative": kwargs.get('live_portrait_relative', True),
                "live_portrait_vx_ratio": kwargs.get('live_portrait_vx_ratio', 0),
                "live_portrait_vy_ratio": kwargs.get('live_portrait_vy_ratio', -0.12),
                "live_portrait_stitching": kwargs.get('live_portrait_stitching', True),
                "video_select_every_n_frames": kwargs.get('video_select_every_n_frames', 1),
                "live_portrait_eye_retargeting": kwargs.get('live_portrait_eye_retargeting', False),
                "live_portrait_lip_retargeting": kwargs.get('live_portrait_lip_retargeting', False),
                "live_portrait_lip_retargeting_multiplier": kwargs.get('live_portrait_lip_retargeting_multiplier', 1),
                "live_portrait_eyes_retargeting_multiplier": kwargs.get('live_portrait_eyes_retargeting_multiplier', 1)
            }
        }
