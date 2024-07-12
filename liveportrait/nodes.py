import os
import sys
import json
import subprocess
import numpy as np
import re
import datetime
from typing import List
import torch
from PIL import Image, ExifTags
from PIL.PngImagePlugin import PngInfo
from pathlib import Path
from string import Template
import itertools

import folder_paths
from .logger import logger
from .image_latent_nodes import *
from .load_video_nodes import LoadVideoUpload, LoadVideoPath
from .load_images_nodes import LoadImagesFromDirectoryUpload, LoadImagesFromDirectoryPath
from .batched_nodes import VAEEncodeBatched, VAEDecodeBatched
from .utils import ffmpeg_path, get_audio, hash_path, validate_path, requeue_workflow, gifski_path, calculate_file_hash, strip_path
from comfy.utils import ProgressBar

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
