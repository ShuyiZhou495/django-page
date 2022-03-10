from scipy.spatial.transform import Rotation as R
import numpy as np
from calibration.funcs.base.camera import Camera


class BaseTransform():
    type = None
    cam: Camera

    def __init__(self, config=None):
        self.config = config

    def toCamera(self, p3d, excalib):
        """
        lidar space to camera space with reflectivity or something else.

        delete the points with z < 0.

        :param p3d: np.array([[[x], [y], [z], [r]...]])
        :param excalib: np.array([radian, radian, radian, x, y, z])
        :return: np.array([[[x], [y], [z], [r]...]])
        """
        p = p3d.copy()
        p[:, 0:3] = np.matmul(
            R.from_quat(excalib[0:4]).as_matrix(),
            p[:, 0:3]
        ) + excalib[4:7].reshape((3, 1))
        return p[p[:, 2, 0] > 0] if self.cam.type != "Omnidirectional" else p

    def toImage(self, p3d, excalib) -> np.ndarray:
        """
        lidar 3d points to camera image
        :param p3d:
        :param excalib:
        :return:  [[u, v, r, z]]
        """
        p3d = self.toCamera(p3d, excalib)
        return self.cam.toImage(p3d)

    def toImageAndFilter3dPoints(self, p3d, excalib):
        """
        return p3d in camera space corresponding to p2d in image

        :param p3d:
        :param excalib:
        :return:
        """
        p3 = self.toCamera(p3d, excalib)
        p2 = self.cam.to2dPoint(p3)
        filter = self.cam.filter2dPoint(p2)
        return p3[filter], p2[filter]


    # def findGoodPoints(self, frame: Frame):
    #     """
    #     find features by cv2.goodFeaturesToTrack;
    #     since in features position are found as integer, add the difference from integer directly to the featured points
    #     point3d_feature is corresponding feature and point2d_feature are corresponding variables in frame
    #
    #     :param frame: old frame
    #     :return: write in frame.point3d_feature and frame.point2d_feature
    #     """
    #     grey_frame = cv2.cvtColor(frame.img, cv2.COLOR_BGR2GRAY)
    #
    #     mask = np.zeros((frame.img.shape[0], frame.img.shape[1]), np.uint8)
    #     for i in range(frame.point2d.shape[0]):
    #         p = frame.point2d[i]
    #         mask[int(p[1]): int(p[1]) + 2, int(p[0]): int(p[0]) + 2] = 255
    #
    #     features = cv2.goodFeaturesToTrack(grey_frame, 200, .1, 40, mask=mask)  # features returned are integers
    #     # feature - shape of (len, 1, 2)
    #     point2d_feature = []
    #     point3d_feature = []
    #     for i in range(frame.point2d.shape[0]):
    #         f = features - frame.point2d[i][0:2]
    #         for j in range(f.shape[0]):
    #             if abs(f[j, 0, 0]) < 1 and abs(f[j, 0, 1]) < 1:
    #                 point2d_feature.append(
    #                     [frame.point2d[i][0] + f[j, 0, 0], frame.point2d[i][1] + f[j, 0, 1], frame.point2d[i][2]])
    #                 point3d_feature.append(frame.point3d[i])
    #     frame.point3d_feature = np.array(point3d_feature)
    #     frame.point2d_feature = np.array(point2d_feature)
    #
    # def tracker(self, old: Frame, new: Frame):
    #     """
    #     v_k
    #     :param old:
    #     :param new:
    #     :param findGood: if false, use point2d directly
    #     :return: set new.point2d_feature
    #     """
    #     if self.findGood:
    #         self.findGoodPoints(old)
    #         features_next, status, _ = cv2.calcOpticalFlowPyrLK(old.img, new.img,
    #                                                             old.point2d_feature[:, 0:2].astype(np.float32).reshape(
    #                                                                 (-1, 1, 2)), None)
    #         new.point2d_feature = np.concatenate(
    #             (features_next.reshape(-1, 2), old.point2d_feature[:, 2].reshape(-1, 1)), axis=1)
    #
    #     else:
    #         features_next, status, _ = cv2.calcOpticalFlowPyrLK(old.img, new.img,
    #                                                             old.point2d[:, 0:2].astype(np.float32).reshape(
    #                                                                 (-1, 1, 2)), None)
    #         new.point2d_feature = np.concatenate((features_next.reshape(-1, 2), old.point2d[:, 2].reshape(-1, 1)),
    #                                              axis=1)
    #
    def calibEx(self, excalib):
        """
        implement in each method
        :param excalib:
        :return:
        """
        pass
