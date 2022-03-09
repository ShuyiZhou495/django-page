from calibration.funcs.base.oneFrameBase import OneFrameBase
import cv2.cv2 as cv2
import numpy as np
import matplotlib.pyplot as plt

class Histogram():

    def __init__(self):
        self.x, self.y = np.zeros((256,)), np.zeros((256,))
        self.xy = np.zeros((256, 256))
        self.count = 0
        self.x_sum, self.y_sum = 0, 0

    def addData(self, intensity, reflectivity):
        """
        create histogram by two variables

        :param intensity: np.array of shape (-1,)
        :param reflectivity: np.array of shape (-1,)
        """
        for i in range(intensity.shape[0]):
            self.x[intensity[i]] += 1
            self.y[reflectivity[i]] += 1
            self.xy[intensity[i], reflectivity[i]] += 1
            self.count += 1
            self.x_sum += intensity[i]
            self.y_sum += reflectivity[i]

    def pltKDE(self):
        plt.cla()
        plt.close()
        fig, axs = plt.subplots(2, 2)
        axs[0, 0].plot(np.arange(256), self.x)
        axs[0, 0].plot(np.arange(256), self.px)
        axs[0, 0].set_title('image intensity')
        axs[0, 1].plot(np.arange(256), self.y)
        axs[0, 1].plot(np.arange(256), self.py)
        axs[0, 1].set_title('reflectivity')
        axs[1, 0].imshow(self.xy)
        axs[1, 1].imshow(self.pxy)
        axs[1, 1].set_title('smoothed')


    def calKDE(self):
        """
        calculate probabilities and save to self.px, self.py, self.pxy
            - px: possibility of variable X for image intensity;
            - py: possibility of variable Y for reflectivity;
            - pxy: possibility of X, Y
        """
        mu_x = self.x_sum / self.count
        mu_y = self.y_sum / self.count
        self.x /= self.count
        self.y /= self.count
        self.xy /= self.count
        sigma_x, sigma_y = 0, 0
        for i in range(256):
            sigma_x = sigma_x + (self.x[i]*(i - mu_x)*(i - mu_x))
            sigma_y = sigma_y + (self.y[i]*(i - mu_y)*(i - mu_y))
        sigma_x = 1.06 * np.sqrt (sigma_x)/(self.count ** 0.2)
        sigma_y = 1.06 * np.sqrt (sigma_y)/(self.count ** 0.2)

        self.px = cv2.GaussianBlur(self.x, (0, 0), sigma_x)
        self.py = cv2.GaussianBlur(self.y, (0, 0), sigma_y)
        self.pxy = cv2.GaussianBlur(self.xy, (0, 0), sigmaX=sigma_x, sigmaY=sigma_y)

    def entropy(self, p):
        p[p==0] = 1
        return -np.sum(np.log(p) * p)

    def calMI(self, show_plt):
        self.calKDE()
        if show_plt:
            self.pltKDE()
        return self.entropy(self.px) + self.entropy(self.py) - self.entropy(self.pxy)

class MI(OneFrameBase):
    type = "MI"
    def __init__(self, config):

        super().__init__()
        self.show_plt = config.show_distribution

    def calibEx(self, excalib) -> float:
        h = Histogram()
        for j in range(len(self.frames)):
            frame = self.frames[j]
            frame.point2d = self.toImage(frame.pointcloud.copy(), excalib)
            rounded = np.round(frame.point2d[:, :3]).astype(int)
            intensity = frame.gray[rounded[:, 1], rounded[:, 0]]
            h.addData(intensity, rounded[:, 2])
        mi = h.calMI(self.show_plt)
        return mi
