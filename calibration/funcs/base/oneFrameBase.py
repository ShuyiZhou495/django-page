from calibration.funcs.base.baseTransform import BaseTransform

class OneFrameBase(BaseTransform):
    frames = None

    def __init__(self, config=None):
        super().__init__(config)
