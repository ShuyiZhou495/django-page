from asgiref.sync import sync_to_async
from calibration.funcs.base.camera import FisheyeCam, PinholeCam, PerspectiveCam, OmnidirCam,  Camera
from calibration.funcs.base.frame import FrameTXT, Frame
from calibration.funcs.calibration import Calibration
from calibration.funcs.base.baseTransform import BaseTransform
from calibration.funcs.base.util import state
import random
from calibration.models import Config, Camera as Cam, Lidar
import json

def run(number):
    try:
        ### --- camera setting ----
        config = Config.objects.get(pk=number)
        state('cam', 'start', 'Loading camera parameters')
        cam = Cam.objects.get(pk=config.camera_id)
        if cam.ctype == 'fisheye':
            myCam = FisheyeCam(cam)
        elif cam.ctype  == "pinhole":
            myCam = PinholeCam(cam)
        elif cam.ctype == "omni":
            myCam = OmnidirCam(cam)
        elif cam.ctype == "perspective": # "perspective"
            myCam = PerspectiveCam(cam)
        else:
            state('cam', 'err', 'wrong camera type input')
        state('cam', 'msg', f'load {myCam.type} camera')
        state('cam', 'finish')

        ### --- camera setting ---

        ### --- frame setting ---
        state('frame', 'start', 'Loading frames')
        Frame.frame_info = config
        Frame.laser_num = (Lidar.objects.get(pk=config.lidar_id)).laser_num

        # img, motion parameter and pointclouds are loaded here
        if config.select_frame_by_hand:
            frames = [FrameTXT(f) for f in json.loads(f"[{config.selected}]")]
        else:
            start_frame, end_frame = config.start_frame, config.end_frame
            choices = sorted(random.sample(range(start_frame, end_frame + 1), config.use_frame))
            frames = [FrameTXT(f) for f in choices]
        for frame in frames:
            frame.load()
        state('frame', 'finish')
        ### --- frame setting ---

        # setting of base transform
        BaseTransform.cam = myCam

        # Calibration setup
        myCalibration = Calibration(myCam, frames, config)
        state('calib', 'start', 'Calibrating')
        myCalibration.run()
    finally:
        print('exit')


async def run_async(number):
    ### --- camera setting ----
    config = await sync_to_async(Config.objects.get, thread_sensitive=True)(pk=number)
    await state('cam', 'start', 'Loading camera parameters')
    cam = await sync_to_async(Cam.objects.get, thread_sensitive=True)(pk=config.camera_id)
    if cam.ctype == 'fisheye':
        myCam = FisheyeCam(cam)
    elif cam.ctype  == "pinhole":
        myCam = PinholeCam(cam)
    elif cam.ctype == "omni":
        myCam = OmnidirCam(cam)
    elif cam.ctype == "perspective": # "perspective"
        myCam = PerspectiveCam(cam)
    else:
        await state('cam', 'err', 'wrong camera type input')
    await state('cam', 'msg', f'load {myCam.type} camera')
    await state('cam', 'finish')

    ### --- camera setting ---

    ### --- frame setting ---
    await state('frame', 'start', 'Loading frames')
    Frame.frame_info = config
    Frame.laser_num = (await sync_to_async(Lidar.objects.get, thread_sensitive=True)(pk=config.lidar_id)).laser_num

    # img, motion parameter and pointclouds are loaded here
    if config.select_frame_by_hand:
        frames = [FrameTXT(f) for f in json.loads(f"[{config.selected}]")]
    else:
        start_frame, end_frame = config.start_frame, config.end_frame
        choices = sorted(random.sample(range(start_frame, end_frame + 1), config.use_frame))
        frames = [FrameTXT(f) for f in choices]
    for frame in frames:
        await frame.load()
    await state('frame', 'finish')
    ### --- frame setting ---

    # setting of base transform
    BaseTransform.cam = myCam

    # Calibration setup
    myCalibration = Calibration(myCam, frames, config)
    await state('calib', 'start', 'Calibrating')
    # await myCalibration.run()
