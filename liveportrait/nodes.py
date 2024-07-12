import os

import folder_paths

from .image_latent_nodes import *
from .load_video_nodes import LoadVideoUpload

folder_paths.folder_names_and_paths["VHS_video_formats"] = (
    [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video_formats"),
    ],
    [".json"]
)
audio_extensions = ['mp3', 'mp4', 'wav', 'ogg']


NODE_CLASS_MAPPINGS = {
    "VHS_LoadVideo": LoadVideoUpload,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "VHS_LoadVideo": "Load Video (Upload) 🎥🅥🅗🅢"
}
