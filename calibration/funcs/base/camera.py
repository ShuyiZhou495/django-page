import numpy as np
from scipy.spatial.transform import Rotation as R
from sympy import symbols, Eq, solveset, Interval
import cv2.cv2 as cv2
class Camera:
    type = None
    k = None
    dist = None
    excalib = None

    def __init__(self, param):
        self.height, self.width = param.height, param.height
        if param.mask:
            self.mask = cv2.imread(param.mask, cv2.IMREAD_GRAYSCALE)
        else:
            self.mask = None

    def init_excalib(self, param):
        res = np.array([0,0,0,0,param.t1, param.t2, param.t3])
        if param.ini_type == "euler":
            r = [param.R1, param.R2, param.R3]
            res[0: 4] = R.from_euler("xyz", r, degrees=param.degree).as_quat()
        elif param.ini_type == "quaternion":
            res[0: 4] = [param.R1, param.R2, param.R3, param.R4]
        else:
            assert False, "'type' is only expected to be 'euler' or 'quaternion'"
        return res

    def to2dPoint(self, point_3d) -> np.ndarray:
        """
        camera space 3d to image 2d point,


        :param point_3d: any shape including contents of [x, y, z, r]
        :return: [[u, v, r, z]]
        """
        p2s = self.inner_trans(point_3d[:, 0: 3])
        p2s = np.hstack((p2s.reshape((-1, 2)), point_3d[:, 3:1:-1].reshape((-1, 2))))
        return p2s

    def filter2dPoint(self, p2s):
        """
        points out of frame height/width are deleted

        :param p2s: [[u, v, r, z]]
        :return: filter
        """
        filter = (p2s[:, 0] < self.width - 1) & (p2s[:, 1] < self.height - 1) & (p2s[:, 0] > 0) & (p2s[:, 1] > 0)
        if self.mask is not None:
            rounded = np.round(p2s[:, 0: 2]).astype(int)
            filter = filter & (self.mask[rounded[:, 1], rounded[:, 0]] != 0)
        return filter

    def toImage(self,  point_3d):
        p2d = self.to2dPoint(point_3d)
        filter = self.filter2dPoint(p2d)
        return p2d[filter]


    def inner_trans(self, point_3d: np.ndarray) -> np.ndarray:
        pass

    def inv_inner_trans(self, point_2d: np.ndarray):
        pass

    def undistort_points(self, p2):
        pass



class FisheyeCam(Camera):
    type = "Fisheye"
    def __init__(self, param):
        super().__init__(param)
        self.cx, self.cy, self.f = param["cx"], param["cy"], param["f"]
        self.b1, self.k1, self.k2, self.k3 = param["b1"], param["k1"], param["k2"], param["k3"]

    def inv_inner_trans(self, point_2d: np.ndarray):
        """

        :param point_2d: point in 2d as np.array of shape (2,)
        :return: (3, 1)
        """
        u, v = point_2d.reshape((2,))
        xd, yd = (u-self.cx)/(self.f + self.b1), (v - self.cy) / self.f
        x = symbols('x')
        eq = Eq(x + self.k1 * x ** 3 + self.k2 * x ** 5 + self.k3 * x ** 7 - np.sqrt(xd**2 + yd**2), 0)
        sol = solveset(eq, x, Interval(0, np.pi/2))
        if(len(sol) == 0):
            return np.array([])
        theta = list(sol)[0]
        r0 = np.tan(float(theta))
        ratio = xd / yd
        y0 = (r0 / (ratio ** 2 + 1)) ** 0.5
        if yd < 0:
            y0 = -y0
        x0 = ratio * y0
        return np.array([[x0], [y0], [1]]) / np.sqrt(x0**2 + y0**2 +1)

    def inner_trans(self, point_3d: np.ndarray) -> np.ndarray:
        """
        inner calibration transform of fisheye
        :param point_3d: np.array of shape (3, 1)
        :return: point in 2d as np.array of shape (2,)
        """
        point_3d = point_3d.reshape((3, -1))
        x0, y0 = point_3d[:, 0] / point_3d[:, 2], point_3d[:, 1] / point_3d[:, 2]
        r0 = -np.sqrt(x0 * x0 + y0 * y0) * (((point_3d[:, 2] > 0).astype(float) - 0.5) * 2).astype(int)
        theta = np.arctan(r0)
        theta[theta < 0] = theta[theta < 0] + np.pi
        x_, y_ = x0 / r0 * theta, y0 / r0 * theta

        distv = (1 + self.k1 * theta ** 2 + self.k2 * theta ** 4 + self.k3 * theta ** 6)
        xd, yd = x_ * distv, y_ * distv
        u, v = self.cx + xd * self.f + xd * self.b1, self.cy + yd * self.f
        return np.column_stack((u, v))

class PinholeCam(Camera):
    type = "Pinhole"
    def __init__(self, param):
        super().__init__(param)
        self.k = np.array([
            [param["f"] * param["sx"], 0, param["cx"]],
            [0, param["f"] * param["sy"], param["cy"]],
            [0, 0, 1]
        ])

    def inner_trans(self, point_3d: np.ndarray)-> np.ndarray:
        p = np.matmul(self.k, point_3d.reshape((-1, 3, 1))).reshape((-1,3))
        p[:,0] /= p[:, 2]
        p[:,1] /= p[:, 2]
        return p[:, 0:2]


    def inv_inner_trans(self, point_2d: np.ndarray):
        point_3d = np.row_stack(point_2d.reshape((2, 1)), np.ones((1, 1)))
        return np.matmul(np.linalg.inv(self.k), point_3d)

class PerspectiveCam(Camera):
    type = "Perspective"
    def __init__(self, param):
        super().__init__(param)
        self.k = np.array(param["k"])
        self.dist = np.array(param["dist"])

    def inner_trans(self, point_3d: np.ndarray):
        p2s, _ = cv2.projectPoints(point_3d.reshape((-1, 1, 3)), np.eye(3), np.zeros((3,1)), self.k, self.dist)
        return p2s

    def inv_inner_trans(self, point_2d: np.ndarray):
        pass

    def undistort(self, img):
        return cv2.undistort(img, self.k, self.dist)

    def undistort_points(self, p2):
        return cv2.undistortPoints(p2.astype("float64"), self.k, self.dist)

class OmnidirCam(Camera):
    type = "Omnidirectional"
    def __init__(self, param):
        super().__init__(param)

    def inner_trans(self, point_3d: np.ndarray) -> np.ndarray:
        point_3d = point_3d.reshape((-1, 3))
        r = np.linalg.norm(point_3d, axis=1)
        theta = np.arctan2(point_3d[:, 1], point_3d[:, 0])
        phi = np.arccos(point_3d[:, 2] / r)
        x = (-theta + np.pi) * self.width / (np.pi * 2)
        y = phi / np.pi * self.height
        return np.column_stack((x, y))

    # def undistort_points(self, p2):
    #     return 	cv2.omnidir.undistortPoints(p2.astype("float64"), self.k, self.dist, self.xi, np.eye(3))
