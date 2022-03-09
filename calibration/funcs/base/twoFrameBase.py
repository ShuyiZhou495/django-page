from calibration.funcs.base.baseTransform import BaseTransform
from scipy.spatial.transform import Rotation as R
from calibration.funcs.base.frame import Frame
from calibration.funcs.base.util import *

class TwoFrameBase(BaseTransform):
    frame1: Frame
    frame2: Frame

    def __init__(self, config):
        super().__init__(config)
        self.check_tracked = config["check_tracked"]
        self.frame1to2_motion = None
        self.frame2to1_motion = None

    def prepare_for_ego(self):
        if self.frame1to2_motion is None:
            self.frame1to2_motion = self.__track__(self.frame1, self.frame2, self.cam.excalib, True)
        else:
            _ = self.__track__(self.frame1, self.frame2, self.cam.excalib, True)

    def inv_motion(self, motion):
        matrix = np.zeros((4, 4))
        matrix[0:3, 0:3] = R.from_quat(motion[0:4]).as_matrix()
        matrix[0:3, 3] = motion[4: 7]
        matrix[3, 3] = 1
        inv = np.linalg.inv(matrix)
        return np.hstack(
            (
                R.from_matrix(inv[0:3, 0:3]).as_quat(),
                inv[0:3, 3].reshape((3, ))
            )
        )

    def prepare_for_ex(self):
        self.frame2to1_motion = self.inv_motion(self.frame1to2_motion)


    def __set_undistort__(self):
        if self.frame1.undistort_img is None:
            self.frame1.undistort_img = self.cam.undistort(self.frame1.img)
        if self.frame2.undistort_img is None:
            self.frame2.undistort_img = self.cam.undistort(self.frame2.img)

    def __track__(self, from_frame: Frame, to_frame: Frame, excalib, estimate_pose=False):

        # transfer to camera space and camera image
        p3d, p2d = self.toImageAndFilter3dPoints(from_frame.pointcloud, excalib)

        # track to next frame, fil ter untracked
        fea1 = p2d[:, 0: 2].reshape((-1, 1, 2)).astype(np.float32)
        fea2, status, _  = cv2.calcOpticalFlowPyrLK(from_frame.img, to_frame.img, fea1, None)
        p3d = p3d[status[:, 0] == 1]
        p2d = p2d[status[:, 0] == 1]
        fea1 = fea1[status[:, 0] == 1]
        fea2 = fea2[status[:, 0] == 1]

        if estimate_pose:
            # calculate essential matrix, filter outliers
            E, mask = cv2.findEssentialMat(fea1, fea2, self.cam.k, cv2.RANSAC, 0.999, 1)
            p3d = p3d[mask[:, 0] == 1]
            p2d = p2d[mask[:, 0] == 1]
            fea1 = fea1[mask[:, 0] == 1]
            fea2 = fea2[mask[:, 0] == 1]

            # matching rotation and translation, filter outliers
            count, Rot, t, mask = cv2.recoverPose(E, fea1, fea2, self.cam.k)
            p3d = p3d[mask[:, 0] == 255]
            p2d = p2d[mask[:, 0] == 255]
            fea2 = fea2[mask[:, 0] == 255]

        from_frame.point3d_feature = p3d
        from_frame.point2d_to_track = p2d

        p2d[:, 0:2] = fea2.reshape(-1, 2)
        to_frame.point2d_tracked = p2d

        if self.check_tracked:
            draw_circles(img=from_frame.img,
                         centers=from_frame.point2d_to_track,
                         color=[255, 255, 0],
                         radius=4,
                         title=f"before tracking",
                         wait=0
                         )
            draw_circles(img=to_frame.img,
                         centers=to_frame.point2d_tracked,
                         color=[255, 255, 0],
                         radius=4,
                         title=f"after tracking",
                         wait=0
                         )
        if estimate_pose:
            return np.hstack(
                (
                    R.from_matrix(Rot).as_euler('xyz'),
                    t.reshape((3, ))
                )
            )

    def applyMotion(self, p3d, motion):
        p = p3d.copy()
        p[:, 0:3] = np.matmul(
            R.from_quat(motion[0:4]).as_matrix(),
            p[:, 0:3]
        ) + motion[4:7].reshape((3, 1))

        return p