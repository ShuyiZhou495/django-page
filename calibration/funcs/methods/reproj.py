import numpy as np
from calibration.funcs.base.twoFrameBase import TwoFrameBase
from scipy.spatial.transform import Rotation as R
import cv2.cv2 as cv2

class Reproj(TwoFrameBase):
    type = "Reproj"

    def __init__(self, config):

        super().__init__(config)
        self.__lambda__ = 0.5

    def calEgo(self, motion):
        point1 = self.cam.undistort_points(self.frame1.point2d_to_track[:, 0:2])
        point2 = self.cam.undistort_points(self.frame2.point2d_tracked[:, 0:2])
        epi = self.epipolar(motion, point1, point2)
        repro = self.__reproject_err__(self.frame1, self.frame2, motion)
        return epi, repro, repro + self.__lambda__ * epi

    def __reproject_err__(self, frame1, frame2, motion):
        p = self.applyMotion(frame1.point3d_feature, motion)
        frame2.point2d_motion = self.cam.to2dPoint(p)
        diff = frame2.point2d_motion - frame2.point2d_tracked
        cost = np.linalg.norm(diff[:, [0, 1, 3]], axis=1)
        cost =  - np.linalg.norm(cost)/np.sqrt(cost.shape[0])
        return cost

    def calibEx(self, excalib):
        self.__track__(self.frame2, self.frame1, excalib, True)
        return self.__reproject_err__(self.frame2, self.frame1, self.frame2to1_motion)

    def Sampson(self, x: np.ndarray, xp: np.ndarray, F: np.ndarray):
        """

        :param x: 3
        :param xp: 3
        :param F: 3x3
        :return:
        """
        x = x.reshape((3, 1))
        xp = xp.reshape((1, 3))
        F = F.reshape((3, 3))
        Fx = np.matmul(F, x)
        xpF = np.matmul(xp, F.transpose())
        xpFx = np.matmul(xp, Fx)
        return xpFx[0, 0] / (Fx[0, 0] + Fx[1, 0] + xpF[0, 0] + xpF[0, 1])

    def epipolar(self, motion, point1, point2):
        """

        :param point1: (-1, 2)
        :param point2: (-1, 2)
        :return:
        """
        t1, t2, t3 = motion[3], motion[4], motion[5]
        t_s = np.array([
            [0, -t3, t2],
            [t3, 0, -t1],
            [-t2, t1, 0]
        ])
        Rot = R.from_euler('xyz', motion[0: 3]).as_matrix()
        F = np.matmul(self.cam.k.transpose(), t_s)
        F = np.matmul(F, Rot)
        F = np.matmul(F, np.linalg.inv(self.cam.k))
        point1 = point1.reshape((-1, 2))
        point2 = point2.reshape((-1, 2))
        epi = 0
        for i in range(point1.shape[0]):
            epi += self.Sampson(
                np.array([point1[i, 0], point1[i, 1], 1]),
                np.array([point2[i, 0], point2[i, 1], 1]),
                F) ** 2
        return -np.sqrt(epi)


