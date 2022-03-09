import json
from calibration.funcs.base.camera import FisheyeCam, PinholeCam, PerspectiveCam, OmnidirCam,  Camera
from calibration.funcs.base.frame import FrameTXT, Frame
from calibration.funcs.calibration import Calibration
from calibration.funcs.base.baseTransform import BaseTransform
import platform
import sys
import random
from models import Config

def run(config: Config):

    if config.camera.ctype == 'fisheye':
        myCam = FisheyeCam(config.camera)
    elif config.camera.ctype  == "pinhole":
        myCam = PinholeCam(config.camera)
    elif config.camera.ctype == "omni":
        myCam = OmnidirCam(config.camera)
    else: # "perspective"
        myCam = PerspectiveCam(config.camera)

    # setting of frame
    Frame.frame_info = config

    # img, motion parameter and pointclouds are loaded here
    if config.select_frame_by_hand:
        frames = [FrameTXT(f) for f in json.loads(f"[{config.selected}]")]
    else:
        start_frame, end_frame = config.start_frame, config.end_frame
        choices = sorted(random.sample(range(start_frame, end_frame + 1), config.use_frame))
        frames = [FrameTXT(f) for f in choices]

    # setting of base transform
    BaseTransform.cam = myCam

    # Calibration setup
    myCalibration = Calibration(myCam, frames, config)

    myCalibration.run()

