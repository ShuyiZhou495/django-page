import numpy as np
from calibration.funcs.base.oneFrameBase import OneFrameBase
from calibration.funcs.base.frame import Frame
from calibration.funcs.base.util import state

import os
import threading
import time
import datetime
import cv2.cv2 as cv2

class Edge(OneFrameBase):
    type = "Edge"
    pause_ = False
    def __init__(self, config):
        super().__init__(config)
        self.__edge_path__ = config.edge_path
        self.__discon = config.discontinuity
        self.__scale__ = 150
        if config.check_laser:
            self.__check_laser__()
        for frame in self.frames:
            self.__prepare_img_edge__(frame)
            self.__detect_scan_edge__(frame)

    def __check_laser__(self):
        frame = self.frames[0]
        try:
            for n, beams in enumerate(frame.beams):
                if n < 64:
                    continue
                p = frame.img.copy()
                p2d = self.toImage(beams, self.cam.excalib)
                for i in range(p2d.shape[0]):
                    cv2.circle(p, (p2d[i, 0:2]).astype(np.int), 2, (255, 255, 0), -1)
                    pr = cv2.resize(p, (1000, int(1000 / p.shape[1] * p.shape[0])))
                    cv2.imshow(f"beam {n}", pr)
                    cv2.waitKey(1)
                cv2.destroyAllWindows()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            return

    def __cal_a_pixel__(self, i, frame):
        sx, ex = i - self.__scale__, i + self.__scale__ + 1
        gsx, gex = 0, self.__scale__ * 2 + 1
        if sx < 0:
            gsx = -sx
            sx = 0

        if ex > frame.img.shape[0] - 1:
            gex += frame.img.shape[0] - 1-ex
            ex = frame.img.shape[0] - 1

        for j in range(frame.img.shape[1]):
            gsy, gey = 0, self.__scale__ * 2 + 1
            sy, ey = j - self.__scale__, j + self.__scale__ + 1
            if sy < 0:
                gsy = -sy
                sy = 0

            if ey > frame.img.shape[1] - 1:
                gey += frame.img.shape[1] - 1 - ey
                ey = frame.img.shape[1] - 1
            frame.D[i, j] = self.__alpha__ * frame.edge[i, j] + (1 - self.__alpha__) * np.max(frame.edge[sx:ex, sy:ey] * self.__gamma_pow__[gsx:gex, gsy:gey])
        state('frame', 'edge-inv', f'{int(i / frame.img.shape[0] * 100)}')
        print(f"\r{i} / {frame.img.shape[0]}; time cost: {str(datetime.timedelta(seconds=int(time.time() - self.__stime__)))}", end="")

    def __cal_img_edge_inv__(self, frame: Frame):
        # ---inverse distance transform---
        path_name = self.__edge_path__ + f"edge_inv_{frame.num:04}" + ".npy"
        if os.path.exists(path_name):
            state('frame', 'msg', f"loading edge_inv for frame {frame.num}")
            print(f"loading edge_inv for frame {frame.num}")
            D = np.load(path_name, allow_pickle=True)
            if D is None or D.shape[0] < frame.img.shape[0]:
                si = D.shape[0] if D is not None else 0
                state('frame', 'msg', f"file is not complete, calculating from the {si}th line")
                state('frame', 'edge-inv-start', f'{int(si/frame.img.shape[0] * 100)}')
                print(f"file is not complete, calculating from the {si}th line")
                frame.D = np.zeros(frame.edge.shape)
                frame.D[:si] = D
            else:
                frame.D = D
                return
        else:
            si = 0
            frame.D = np.zeros(frame.edge.shape)
            state('frame', 'msg', f"calculating edge_inv for frame {frame.num}")
            state('frame', 'edge-inv-start', f"0")
            print(f"calculating edge_inv for frame {frame.num}")
        # -- initialize variables
        self.__alpha__ = 1/3
        gamma = 0.98
        # -- restrict to calculate distance ranged in [-300, 300] to minimize running time
        z = np.zeros((self.__scale__ * 2 + 1, self.__scale__ * 2 + 1))
        for i in range(self.__scale__ * 2 + 1):
            for j in range(self.__scale__ * 2 + 1):
                z[i, j] = max(abs(self.__scale__-i), abs(self.__scale__-j))
        # -- making kernel: gamma ** max(|x-i|, |y-j|) for 600 * 600 pixels
        self.__gamma_pow__ = gamma ** z

        # -- regulating i to 500-1500 (row), j to 500-2000 (column)
        # -- point2d will be filtered out if it is out of the range
        thread_num = 16 # <-- change here
        self.__stime__ = time.time()
        if thread_num == 1:
            for i in range(si, frame.img.shape[0]):
                if not self.pause_:
                    state('frame', 'edge-inv', f'{int(i / frame.img.shape[0] * 100) }')
                    print(f"\r{i} / {frame.img.shape[0]}; time cost: {str(datetime.timedelta(seconds=int(time.time() - self.__stime__)))}", end="")
                    self.__cal_a_pixel__(i, frame)
                else:
                    state('frame', 'err', f'save file till line {i-1}')
                    print('\n' + f'save file till line {i-1}')
                    np.save(path_name, frame.D[:i-1])
                    return
        else:
            for i in range(si, frame.img.shape[0], thread_num):
                if not self.pause_:
                    threads = []
                    for c in range(thread_num):
                        if(c + i >= frame.img.shape[0]):
                            break
                        threads.append(threading.Thread(target=self.__cal_a_pixel__, args=(i + c, frame)))
                        threads[-1].start()
                    for c in range(len(threads)):
                        threads[c].join()
                else:
                    state('frame', 'err', f'save file till line {i-thread_num}')
                    print('\n' + f'save file till line {i-thread_num}')
                    np.save(path_name, frame.D[:i-thread_num])
                    return
            print()
        np.save(path_name, frame.D)

    def __detect_img_edge__(self, frame: Frame):
        # ---edge----
        path_name = self.__edge_path__ + f"edge_{frame.num:04}" + ".png"
        if os.path.exists(path_name):
            print(f"loading edge for frame {frame.num}")
            state('frame', 'msg', f"loading edge for frame {frame.num}")
            frame.edge = cv2.imread(path_name, cv2.IMREAD_GRAYSCALE)
        else:
            print(f"calculating edge for frame {frame.num}")
            state('frame', 'msg', f"calculating edge for frame {frame.num}")

            img = frame.gray.astype(int)
            state('frame', 'edge-start', '0')
            frame.edge = np.zeros(img.shape)
            # -- each pixel is set to the largest absolute value of the difference between it and any of its 8 neighbors
            for i in range(1, img.shape[0] - 2):
                print(f"\r\t{i} / {img.shape[0]}", end="")
                state('frame', 'edge', f'{int(i/img.shape[0] * 100)}')
                for j in range(1, img.shape[1] - 2):
                    p = img[i, j]
                    frame.edge[i, j] = max(
                        abs(img[i - 1, j - 1] - p),
                        abs(img[i, j - 1] - p),
                        abs(img[i + 1, j - 1] - p),
                        abs(img[i - 1, j] - p),
                        abs(img[i + 1, j] - p),
                        abs(img[i - 1, j + 1] - p),
                        abs(img[i, j + 1] - p),
                        abs(img[i + 1, j + 1] - p),
                    )
            print('\r')
            cv2.imwrite(path_name, frame.edge)
        # ---edge----

    def __prepare_img_edge__(self, frame:Frame):
        self.__detect_img_edge__(frame)
        self.__cal_img_edge_inv__(frame)

    def __detect_scan_edge__(self, frame: Frame):
        discon = self.__discon
        edge_points = []

        for points in frame.beams:
            distance = np.linalg.norm(points[:, 0:3], axis=1).reshape((-1, ))
            for i in range(1, distance.shape[0] - 1):
                x = max(distance[i - 1] - distance[i], distance[i + 1] - distance[i], 0)
                x = 0 if x < discon else x ** 0.5
                if x == 0:
                    continue
                edge_points.append([[points[i, 0, 0]], [points[i, 1, 0]],[ points[i, 2, 0]], [x]])
        frame.scan_edge = np.array(edge_points)

    def __calX__(self, excalib, frame: Frame):
        frame.X = np.zeros(frame.gray.shape)
        frame.point2d_edge = self.toImage(frame.scan_edge, excalib)
        rounded = np.round(frame.point2d_edge[:, 0:2]).astype(int)
        frame.X[rounded[:, 1],  rounded[:, 0]] = frame.point2d_edge[:, 2] / (0.1 * frame.point2d_edge.shape[0] * 255)

    def calibEx(self, excalib):
        J = 0
        for frame in self.frames:
            self.__calX__(excalib, frame)
            J += np.sum(frame.X * frame.D)
        return J / len(self.frames)
