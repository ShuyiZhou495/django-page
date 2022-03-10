import json
import numpy as np
import cv2
from . import util
from asgiref.sync import async_to_sync
from scipy.spatial.transform import Rotation as R

class Frame:
    """
    point3d - after extrinsic calibration and z > 0
    point2d - point3d directly transformed by fisheye intrinsic calibration
    point3d_feature - for old frame, it is point3d corresponding to the feature detected
    point2d_feature - for old frame, it is point2d corresponding to the feature detected;
                        for new frame, it is the tracked points.
    point2d_motion - point3d applied by motion and fisheye transform
    """

    # some path or common info
    frame_info = None
    laser_num = None

    def __init__(self, num):

        # common

        self.num = num
        self.point2d = None
        self.img = None
        self.gray = None
        self.pointcloud = None

        # for mi

        # for reprojection error
        self.point3d_feature, self.point2d_tracked, self.point2d_motion = None, None, None
        self.point2d_to_track, self.cam_feature_3d, self.undistort_img = None, None, None

        # for edge
        self.img_edge, self.D, self.X, self.edge, self.range, self.scan_edge, self.beams = None, None, None, None, None, None, []
        self.point2d_edge = None




    def load(self):
        self.loadImg() # self.img, self.gray loaded
        self.loadPoints() # self.pointcloud loaded

    def loadImg(self):
        pass

    def loadPoints(self):
        pass

# class FrameOld(Frame):
#     def __init__(self, num):
#         super().__init__(num)
#         # for path in paths.values():
#         #     self.checkPath(path)
#         self.scale = -0.6
#         self.loadMotion()
#         # without intensity, 4*1 array, last number is 1
#         self.point3d_origin = np.concatenate((self.pointcloud[:, 0:3], np.ones((self.pointcloud.shape[0], 1, 1))), axis=1)
#         print("points size for frame {}:".format(self.num), self.pointcloud.shape[0])
#
#     def checkPath(self, path):
#         if not os.path.exists(tmp_dir + path):
#             os.mkdir(tmp_dir + path)
#
#     def loadMotion(self):
#         if self.frame_info["motion_" + self.os]:
#             file_name = tmp_dir + paths['motion'] + "{}.npy".format(self.num)
#             if not os.path.exists(file_name):
#                 # initialize the matrix
#                 self.motion = np.zeros((4, 4))
#                 self.motion[3, 3] = 1
#                 with open(self.frame_info["motion_" + self.os]) as f:
#                     # the num^th line has the motion
#                     for _ in range(self.num):
#                         s = f.readline()
#                 data = s.split()
#                 # save the time
#                 self.time = float(data[-1])
#                 # data[0:3] to Rotation matrix
#                 self.motion[0:3, 0:3] = R.from_euler('XYZ', [float(data[0]), float(data[1]), float(data[2])]).as_matrix()
#                 # data[3:6] to Translation matrix
#                 self.motion[0:3, 3] = [float(data[3]), float(data[4]), float(data[5])]
#                 # save to tmp file
#                 with open(file_name, 'wb') as f:
#                     np.save(f, self.motion)
#                     np.save(f, self.time)
#             else:
#                 with open(file_name, 'rb') as f:
#                     self.motion = np.load(f)
#                     self.time = np.load(f).item()
#
#     def loadImg(self):
#         file_name = tmp_dir + paths['img']+ "{}.npy".format(self.num)
#         img_path = self.frame_info["image"]["path_" + self.os]
#         img_name = f"fisheye_{self.frame_info['image']['start_frame'] + self.num - 1:06d}"
#         if not os.path.exists(file_name):
#             self.img = cv2.imread(img_path + img_name + ".jpg")
#             self.gray = cv2.imread(img_path + img_name + ".jpg", cv2.IMREAD_GRAYSCALE)
#             np.save(file_name, self.img)
#         else:
#             self.img = np.load(file_name)
#             self.gray = cv2.imread(img_path + img_name + ".jpg", cv2.IMREAD_GRAYSCALE)
#
#     def loadPoints(self):
#         file_name = tmp_dir + paths['pc'] + '{}within{}.npy'.format(self.num, self.time_range)
#         scan_path = self.frame_info["scan"]["path_" + self.os]
#         if not os.path.exists(file_name):
#             points = []
#             with open(scan_path) as f:
#                 f.readline() # point numbers, not need here
#                 data = f.readline().split()
#                 while(self.time - float(data[0]) >  self.frame_info["scan"]["time_range"]):
#                     data = f.readline().split()
#                 while(float(data[0]) - self.time <= self.frame_info["scan"]["time_range"]):
#                     points.append([[float(data[1])], [float(data[2])], [float(data[3])], [np.round(float(data[4]) * 256)]])
#                     data = f.readline().split()
#                 self.pointcloud = np.array(points)
#                 np.save(file_name, self.pointcloud)
#         else:
#             self.pointcloud = np.load(file_name)

class FrameTXT(Frame):

    def __init__(self, num):

        super().__init__(num)


    def loadImg(self):
        img_path = self.frame_info.img_path
        img_type = self.frame_info.img_type
        self.img = cv2.imread(img_path + f'{self.num:04}' + img_type)
        self.gray = cv2.imread(img_path + f'{self.num:04}' + img_type, cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            print('img not load')
            util.state('frame', 'err', f'the image is not loaded for {self.num}')

    def loadPoints(self):
        scan_path = self.frame_info.scan_path
        scan_type = '.txt'
        try:
            self.pointcloud = np.loadtxt(scan_path + f'{self.num:04}' + scan_type,
                                         delimiter=self.frame_info.delimiter,
                                         skiprows=self.frame_info.skip_line).reshape((-1, 4, 1))
        except:
            util.state('frame', 'err', f'scan file for frame {self.num} is not found')
            return
        if self.frame_info.rxyz:
            # change the formate to [x, y, z, reflectivity]
            print('rxyz')
            r = self.pointcloud[:, 0].copy()
            self.pointcloud[:, 0:3] = self.pointcloud[:, 1:4]
            self.pointcloud[:, 3] = r
        for i in range(self.laser_num):
            temp = self.pointcloud[i::self.laser_num]
            self.beams.append(temp[(temp != 0).all(axis=1)[:, 0]])

        # delete the points with [0, 0, 0, 0]
        self.pointcloud = self.pointcloud[(self.pointcloud != 0).all(axis=1)[:, 0]]
        util.state('frame', 'msg', f'points size for frame {self.num}: {self.pointcloud.shape[0]}')
        print("points size for frame {}:".format(self.num), self.pointcloud.shape[0])

