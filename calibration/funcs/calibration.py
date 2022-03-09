from calibration.funcs.base.camera import Camera
from calibration.funcs.base.frame import Frame
from calibration.funcs.methods.reproj import Reproj
from calibration.funcs.methods.mi import MI
from calibration.funcs.methods.edge import Edge
from calibration.funcs.base.oneFrameBase import OneFrameBase
from calibration.funcs.base.twoFrameBase import TwoFrameBase
from calibration.funcs.base.util import *
import cv2.cv2 as cv2
import numpy as np
import termcolor
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

class Calibration:

    def __init__(self, cam: Camera, frames: [Frame], config):
        OneFrameBase.frames = frames
        TwoFrameBase.frame1,  TwoFrameBase.frame2 = frames[0], frames[1]

        self.frames = frames

        self.cam = cam

        self.verbose = config.verbose

        self.reproj, self.mi, self.edge, self.loop = None, None, None, 0

        self.use_repro, self.use_edge, self.use_mi = False, config.edge_use, config.mi_use

        self.ex = True

        self.cam.excalib = self.cam.init_excalib(config)

        if self.use_repro:
            self.ex = False
            self.loop = config.loop
            self.reproj = Reproj(config)
        if self.use_mi:
            self.mi = MI(config)
        if self.use_edge:
            self.edge = Edge(config)

        self.vis = config.vis

        self.test = {
            "amount": config.test_amount,
            "R_range": config.R_range,
            "t_range": config.t_range
        }
    def visualizeMotion(self):
        draw_circles_one_image(img=self.frames[1].img,
                               centers=[self.frames[1].point2d_motion, self.frames[1].point2d_tracked],
                               color=[[255, 255, 0], [0, 255, 255]],
                               radius=4,
                               title="blue is by motion",
                               wait= 10
                               )

    def visualizeEX(self):
        frame = self.frames[0]
        r = 4
        if self.vis == "edge-e":
            # show edge
            point2d = [frame.point2d_edge]
            color = [[255, 255, 0]]
            title = "edge"
            img = frame.D.astype(np.uint8)
        elif self.vis == "edge":
            # show edge
            point2d = [frame.point2d_edge]
            color = [[255, 255, 0]]
            title = "edge"
            img = frame.img
        elif self.vis == "mi":
            # show part of the points
            m = np.median(frame.point2d[:, 3])
            r = np.max(frame.point2d[:, 3]) - np.min(frame.point2d[:, 3])
            point2d = [frame.point2d[np.bitwise_and(frame.point2d[:, 3] < m + r / 10, frame.point2d[:, 3] > m - r / 10)]]
            color = [[255, 255 ,0]]
            title = f"depth a range"
            img = frame.img
            r = 2
        elif self.vis == "mi-r":
            m = np.median(frame.point2d[:, 3])
            r = np.max(frame.point2d[:, 3]) - np.min(frame.point2d[:, 3])
            point2d = [frame.point2d[np.bitwise_and(frame.point2d[:, 3] < m + r / 5, frame.point2d[:, 3] > m - r / 5)]]
            color = ["r"]
            title = "color by reflectivity"
            img = frame.img
            r = 2
        else:
            point2d = [frame.point2d_tracked, frame.point2d_motion]
            color = [[255, 255, 0], [0, 255, 255]]
            title = "blue is motion, yellow is tracked points"
            img = frame.img

        draw_circles_one_image(img=img,
                               centers=point2d,
                               color=color,
                               radius=r,
                               title=f"frame {frame.num} " + title,
                               wait= 10
                               )

    def lineToStr(self, cost, mi, edge, r, epi, excalib):
        if self.ex:
            return (f" {cost:10.6f} | " if type(cost) != type("") else f" {cost:10} | ") \
                   + (f"{edge:10.6f} | " if type(edge) != type("") else f"{edge:10} | ") * self.use_edge  \
                   + (f"{mi:10.6f} | " if type(mi) != type("") else f"{mi:10} | ") * self.use_mi \
                   + (f"{r:10.6f} | " if type(r) != type("") else f"{r:10} | ") * self.use_repro \
                   + (f"{excalib[0] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[1] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[2] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[3] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[4]:10.6f} | {excalib[5]:10.6f} | {excalib[6]:10.6f} |"
                      if type(excalib[0]) != type("") else
                      f"{excalib[0]:10} | {excalib[1]:10} | {excalib[2]:10} | "
                      f"{excalib[3]:10} | {excalib[4]:10} | {excalib[5]:10} | "
                      f"{excalib[6]:10} | ")
        else:
            return (f" {cost:10.6f} | " if type(cost) != type("") else f" {cost:10} | ") \
                   + (f"{epi:10.6f} | " if type(epi) != type("") else f"{epi:10} | ") \
                   + (f"{r:10.6f} | " if type(r) != type("") else f"{r:10} | ") \
                   + (f"{excalib[0] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[1] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[2] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[3] / np.linalg.norm(excalib[0:4]):10.6f} | "
                      f"{excalib[4]:10.6f} | "
                      f"{excalib[5]:10.6f} | {excalib[6]:10.6f} |"
                      if type(excalib[0]) != type("") else
                      f"{excalib[0]:10} | {excalib[1]:10} | {excalib[2]:10} | {excalib[3]:10} | "
                      f"{excalib[4]:10} | {excalib[5]:10} | {excalib[6]:10} | ")

    def gradient_descent(self, parameter, func):
        length = 7
        gamma_t_u, gamma_t_l = 0.02, 0.001
        gamma_r_u, gamma_r_l = 0.02, 0.0005
        delta = np.zeros((length,))
        delta[0: (length + 1)//2] = 0.01
        delta[(length + 1)//2: length] = 0.01
        delF, delF_ = np.zeros((length,)), np.zeros((length,))
        MAX_ITER = 300
        index = 0
        self.max_cost = float('-inf')
        para, para_1, best_para = parameter.copy(), parameter.copy(), parameter.copy()
        f_pre = func(para, self.verbose)
        if self.ex:
            self.visualizeEX()
        else:
            self.visualizeMotion()
        while index < MAX_ITER:
            if f_pre > self.max_cost: ##
                self.max_cost = f_pre
                best_para = para.copy()
            for i in range(length):
                _para = para.copy()
                _para[i] += delta[i]
                cost = func(_para, False)
                delF[i] = (cost - f_pre)/delta[i]
            norm_delF_del_trans = np.linalg.norm(delF[(length + 1)//2: length])
            norm_delF_del_rot= np.linalg.norm(delF[0: (length + 1)//2])
            delF[(length + 1)//2:length] /= norm_delF_del_trans
            delF[0:(length + 1)//2] /= norm_delF_del_rot
            delta_trans = np.linalg.norm((para - para_1)[(length + 1)//2:length]) ** 2
            delta_rot = np.linalg.norm((para - para_1)[0:(length + 1)//2]) ** 2
            if delta_trans > 0:
                temp_deno_trans = np.abs(np.dot((para - para_1)[(length + 1)//2:length], (delF - delF_)[(length + 1)//2:length]))
                gamma_t = delta_trans/temp_deno_trans
            else:
                gamma_t = gamma_t_u
            if delta_rot > 0:
                temp_deno_rot = np.abs(np.dot((para - para_1)[0:(length + 1)//2], (delF - delF_)[0:(length + 1)//2]))
                gamma_r = delta_rot/temp_deno_rot
            else:
                gamma_r = gamma_r_u

            if gamma_t > gamma_t_u:
                gamma_t = gamma_t_u
            elif gamma_t < gamma_t_l:
                gamma_t = gamma_t_l

            if gamma_r > gamma_r_u:
                gamma_r = gamma_r_u
            elif gamma_r < gamma_r_l:
                gamma_r = gamma_r_l

            para_1 = para.copy()
            para[(length + 1)//2:length] += gamma_t * delF[(length + 1)//2:length]
            para[0:(length + 1)//2] += gamma_r * delF[0:(length + 1)//2]

            f_curr = func(para)
            if f_curr < f_pre: ##
                para[(length + 1)//2:length] -= gamma_t * delF[(length + 1)//2:length]
                para[0:(length + 1)//2] -= gamma_r * delF[0:(length + 1)//2]
                gamma_r_u /= 1.2
                gamma_r_l /= 1.2
                gamma_t_u /= 1.2
                gamma_t_l /= 1.2
                delta /= 1.1
                index += 1
                if delta[0] < 0.001:
                    break
                else:
                    continue
            f_pre = f_curr
            index += 1
            delF_ = delF.copy()
            if self.verbose:
                state('calib', 'good')
                print(termcolor.colored(self.lineToStr(f_curr, '   ^', '   ^', '   ^', '   ^', para), 'red'))
            if self.ex:
                self.visualizeEX()
            else:
                self.visualizeMotion()
        return best_para

    def calCost(self, excalib, p=True):
        edge, mi, r = 0, 0.1, 0
        edge_co, mi_co, r_co = 1, 1, 1/200
        if self.use_edge:
            edge = self.edge.calibEx(excalib)
        if self.use_mi:
            mi = self.mi.calibEx(excalib)
        if self.use_repro:
            r = self.reproj.calibEx(excalib)

        cost = r * r_co + (mi) * mi_co + (edge) * edge_co

        if self.verbose and p:
            state('calib', 'ing', '<td>' + self.lineToStr(cost, mi, edge, r, 0, excalib).replace('|', '</td><td>') + '</td>')
            print(self.lineToStr(cost, mi, edge, r, 0, excalib))
            if self.use_mi and self.mi.show_plt:
                plt.draw()
                plt.pause(0.01)

        return cost

    def calEgoCost(self, motion, p=True):
        epi, repro, cost = self.reproj.calEgo(motion)
        if p and self.verbose:
            print(self.lineToStr(cost, 0, 0, repro, epi, motion))
            state('calib', 'ing', '<td>' + self.lineToStr(cost, 0, 0, repro, epi, motion).replace('|', '</td><td>') + '</td>')
        return cost

    def calibOneLoop(self):


        if self.ex:

            print("calibrate extrinsic parameter")
            state('calib', 'msg', "calibrate extrinsic parameter")
            state('calib', 'ing1', '<th>' + self.lineToStr('cost', 'mi', 'edge', 'repro', 'epi', ['R[x]', 'R[y]', 'R[z]', 'R[w]', 't[0]', 't[1]', 't[2]']).replace('|', '</th><th>') + '</th>')
            print(
                self.lineToStr('cost', 'mi', 'edge', 'repro', 'epi', ['R[x]', 'R[y]', 'R[z]', 'R[w]', 't[0]', 't[1]', 't[2]']))
            best_res = self.gradient_descent(self.cam.excalib, self.calCost)
            self.cam.excalib = best_res
        else:
            print("calibrate ego motion")
            state('calib', 'msg', "calibrate ego motion")
            state('calib', 'ing1', '<th>' + self.lineToStr('cost', 'mi', 'edge', 'repro', 'epi', ['R[x]', 'R[y]', 'R[z]', 'R[w]', 't[1]', 't[2]']).replace('|', '</th><th>') + '</th>')
            print(
                self.lineToStr('cost', 'mi', 'edge', 'repro', 'epi', ['R[x]', 'R[y]', 'R[z]', 'R[w]', 't[1]', 't[2]']))
            best_res = self.gradient_descent(self.reproj.frame1to2_motion, self.calEgoCost)
            self.reproj.frame1to2_motion = best_res
            cv2.destroyAllWindows()
        print(termcolor.colored(self.lineToStr(self.max_cost, '   -', '   -', '   -', '   -', best_res), 'blue'))
        state('calib', 'res', '<td>' + self.lineToStr(self.max_cost, '   -', '   -', '   -', '   -', best_res).replace('|', '</td><td>') + '</td>')


    def calib(self):
        if self.use_repro:
            for i in range(self.loop):
                print("========loop{}========".format(i + 1))
                self.ex = False
                # ---- --update ego motion-- ------#
                self.reproj.prepare_for_ego()
                self.calibOneLoop()
                # ---- --update ego motion-- ------#

                self.ex = True
                # ---- --update extrinsic-- ------#
                self.reproj.prepare_for_ex()
                self.calibOneLoop()
                # ---- --update extrinsic-- ------#
        else:
            self.calibOneLoop()

    def run(self):
        if self.test["amount"] == 0:
            self.calib()
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        elif self.test["amount"] == -1:
            add = np.linspace(-self.test["t_range"], self.test["t_range"], 50)
            results = np.zeros((50, ))
            zeros = np.zeros((7, ))
            for i in range(50):
                zeros[6] = add[i]
                results[i] = self.calCost(self.cam.excalib + zeros)
            plt.plot(add, results)
            plt.show()

        else:
            initials = np.zeros((self.test["amount"], 7))
            res = np.zeros((self.test["amount"], 7))
            original = self.cam.excalib
            for n in range(self.test["amount"]):
                print(f"=========={n + 1} test=========")
                state('calib', 'msg', f"=========={n + 1} test=========")
                if self.use_repro:
                    self.reproj.frame1to2_motion = None # re-initialize
                rand = np.random.random(7)
                rand[0: 4] = rand[0: 4] * self.test["R_range"] * 2 - self.test["R_range"]
                rand[4: 7] = rand[4: 7] * self.test["t_range"] * 2 - self.test["t_range"]
                self.cam.excalib = original + rand
                initials[n] = self.cam.excalib
                self.calib()
                cv2.destroyAllWindows()
                res[n] = self.cam.excalib

            print("average:", np.average(res, axis=0))
            state('calib', 'msg', f'average: {np.average(res, axis=0)}')
            print("standard deviation", np.std(res, axis=0))
            state('calib', 'msg', f'standard deviation: {np.std(res, axis=0)}')
        state('calib', 'finish')