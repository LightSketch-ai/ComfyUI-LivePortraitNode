# import requests
# from requests.models import PreparedRequest
# from PIL import Image
# import numpy as np
# import torch
# from torchvision.transforms import ToPILImage
# from io import BytesIO
# import os
# import time
#
# API_KEY = os.environ.get("REPLICATE_API_TOKEN")
#
# # Check for API key in file as a backup, not recommended
# try:
#     if not API_KEY:
#         dir_path = os.path.dirname(os.path.realpath(__file__))
#         with open(os.path.join(dir_path, "replicate_api_key.txt"), "r") as f:
#             API_KEY = f.read().strip()
#         # Validate the key is not empty
#         if API_KEY.strip() == "":
#             raise Exception(
#                 f"API Key is required to use Replicate API. \nPlease set the REPLICATE_API_TOKEN environment variable to your API key or place in {dir_path}/replicate_api_key.txt.")
#
# except Exception as e:
#     print(
#         f"\n\n***API Key is required to use Replicate API. Please set the REPLICATE_API_TOKEN environment variable to your API key or place in {dir_path}/replicate_api_key.txt.***\n\n")
#
# ROOT_API = "https://api.replicate.com/v1/predictions"
#
#
# class ClarityBase:
#     API_ENDPOINT = ""
#     POLL_ENDPOINT = ""
#     ACCEPT = ""
#
#     @classmethod
#     def INPUT_TYPES(cls):
#         return cls.INPUT_SPEC
#
#     RETURN_TYPES = ("IMAGE",)
#     FUNCTION = "call"
#     CATEGORY = "Clarity AI"
#
#     def call(self, *args, **kwargs):
#
#         data = None
#
#         # Check for required arguments
#         face_image = kwargs.get('face_image')
#         driving_video = kwargs.get('driving_video')
#
#         if face_image is None or driving_video is None:
#             raise ValueError("Both face_image and driving_video are required.")
#
#         kwargs['comfyui'] = True
#
#         headers = {
#             "Authorization": f"Bearer {API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         if kwargs.get("api_key_override"):
#             headers = {
#                 "Authorization": f"Bearer {kwargs.get('api_key_override')}",
#                 "Content-Type": "application/json"
#             }
#
#         if headers.get("Authorization") is None:
#             raise Exception(
#                 f"No Replicate API key set.\n\nUse your Replicate API key by:\n1. Setting the REPLICATE_API_TOKEN environment variable to your API key\n3. Placing inside replicate_api_key.txt\n4. Passing the API key as an argument to the function with the key 'api_key_override'")
#
#         data = self._get_data(**kwargs)
#
#         req = PreparedRequest()
#         req.prepare_method('POST')
#         req.prepare_url(f"{ROOT_API}", None)
#         req.prepare_headers(headers)
#         req.prepare_body(data=data, files=None)
#         response = requests.Session().send(req)
#
#         if response.status_code == 200:
#             if self.POLL_ENDPOINT != "":
#                 id = response.json().get("id")
#                 timeout = 550
#                 start_time = time.time()
#                 while True:
#                     response = requests.get(f"{ROOT_API}{self.POLL_ENDPOINT}{id}", headers=headers, timeout=timeout)
#                     if response.status_code == 200:
#                         print("took time: ", time.time() - start_time)
#                         if self.ACCEPT == "image/*":
#                             return self._return_image(response)
#                         if self.ACCEPT == "video/*":
#                             return self._return_video(response)
#                         break
#                     elif response.status_code == 202:
#                         time.sleep(10)
#                     elif time.time() - start_time > timeout:
#                         raise Exception("Replicate API Timeout: Request took too long to complete")
#                     else:
#                         error_info = response.json()
#                         raise Exception(f"Replicate API Error: {error_info}")
#             else:
#                 result_image = Image.open(BytesIO(response.content))
#                 result_image = result_image.convert("RGBA")
#                 result_image = np.array(result_image).astype(np.float32) / 255.0
#                 result_image = torch.from_numpy(result_image)[None,]
#                 return (result_image,)
#         else:
#             print("Fehler!! Status Code:", response.status_code)
#             error_info = response.text
#             print("error_info: " + error_info)
#             if response.status_code == 401:
#                 raise Exception(
#                     "Replicate API Error: Unauthorized.\n\nUse your Replicate API key by:\n1. Setting the REPLICATE_API_TOKEN environment variable to your API key\n3. Placing inside replicate_api_key.txt\n4. Passing the API key as an argument to the function with the key 'api_key_override' \n\n \n\n")
#             if response.status_code == 402:
#                 raise Exception(
#                     "Replicate API Error: Not enough credits.\n\nPlease ensure your Replicate API account has enough credits to complete this action. \n\n \n\n")
#             if response.status_code == 400:
#                 raise Exception(f"Replicate API Error: Bad request.\n\n{error_info} \n\n \n\n")
#             else:
#                 raise Exception(f"Replicate API Error: {error_info}")
#
#     def _return_image(self, response):
#         result_image = Image.open(BytesIO(response.content))
#         result_image = result_image.convert("RGBA")
#         result_image = np.array(result_image).astype(np.float32) / 255.0
#         result_image = torch.from_numpy(result_image)[None,]
#         return (result_image,)
#
#     def _return_video(self, response):
#         result_video = response.content
#         return (result_video,)
#
#     def _get_files(self, buffered, **kwargs):
#         return {
#             "image": buffered.getvalue()
#         }
#
#     def _get_data(self, **kwargs):
#         return {
#             "version": "067dd98cc3e5cb396c4a9efb4bba3eec6c4a9d271211325c477518fc6485e146",
#             "input": {
#                 "face_image": open(kwargs.get('face_image'), 'rb'),
#                 "driving_video": open(kwargs.get('driving_video'), 'rb'),
#                 "live_portrait_dsize": kwargs.get('live_portrait_dsize', 512),
#                 "live_portrait_scale": kwargs.get('live_portrait_scale', 2.3),
#                 "video_frame_load_cap": kwargs.get('video_frame_load_cap', 128),
#                 "live_portrait_lip_zero": kwargs.get('live_portrait_lip_zero', True),
#                 "live_portrait_relative": kwargs.get('live_portrait_relative', True),
#                 "live_portrait_vx_ratio": kwargs.get('live_portrait_vx_ratio', 0),
#                 "live_portrait_vy_ratio": kwargs.get('live_portrait_vy_ratio', -0.12),
#                 "live_portrait_stitching": kwargs.get('live_portrait_stitching', True),
#                 "video_select_every_n_frames": kwargs.get('video_select_every_n_frames', 1),
#                 "live_portrait_eye_retargeting": kwargs.get('live_portrait_eye_retargeting', False),
#                 "live_portrait_lip_retargeting": kwargs.get('live_portrait_lip_retargeting', False),
#                 "live_portrait_lip_retargeting_multiplier": kwargs.get('live_portrait_lip_retargeting_multiplier', 1),
#                 "live_portrait_eyes_retargeting_multiplier": kwargs.get('live_portrait_eyes_retargeting_multiplier', 1)
#             }
#         }
#
#
# class ReplicateLivePortrait(ClarityBase):
#     API_ENDPOINT = ""
#     POLL_ENDPOINT = ""
#     ACCEPT = "video/*"
#     INPUT_SPEC = {
#         "required": {
#             "face_image": ("STRING",),
#             "driving_video": ("STRING",),
#         },
#         "optional": {
#             "live_portrait_dsize": ("INT", {"default": 512}),
#             "live_portrait_scale": ("FLOAT", {"default": 2.3}),
#             "video_frame_load_cap": ("INT", {"default": 128}),
#             "live_portrait_lip_zero": ("BOOL", {"default": True}),
#             "live_portrait_relative": ("BOOL", {"default": True}),
#             "live_portrait_vx_ratio": ("FLOAT", {"default": 0}),
#             "live_portrait_vy_ratio": ("FLOAT", {"default": -0.12}),
#             "live_portrait_stitching": ("BOOL", {"default": True}),
#             "video_select_every_n_frames": ("INT", {"default": 1}),
#             "live_portrait_eye_retargeting": ("BOOL", {"default": False}),
#             "live_portrait_lip_retargeting": ("BOOL", {"default": False}),
#             "live_portrait_lip_retargeting_multiplier": ("FLOAT", {"default": 1}),
#             "live_portrait_eyes_retargeting_multiplier": ("FLOAT", {"default": 1}),
#             "api_key_override": ("STRING", {"multiline": False}),
#         }
#     }
