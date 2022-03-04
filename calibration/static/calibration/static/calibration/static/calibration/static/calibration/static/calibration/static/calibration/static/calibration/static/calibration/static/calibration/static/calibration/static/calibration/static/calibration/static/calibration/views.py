from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View, generic
from calibration.models import ConfigForm, CameraForm, LidarForm, Camera, Lidar, Config
import json
import numpy as np

class Index(View):
    template = 'index.html'
    def get(self, request):
        return render(request, self.template)

class Add_config(View):
    template = 'add_config.html'
    json_config_keys = {
        'camera': {
            'all': {'type':'ctype', 'height': 'height', 'width': 'width', 'mask': 'mask'},
            'perspective': ['k', 'dist'],
            'omni': [],
            'fisheye': ['f', 'cx', 'cy', 'k1', 'k2', 'k3', 'b1'],
            'pinhole': ['f', 'cx', 'cy', 'sx', 'sy']
        }
    }

    def get(self, request):
        return render(request, self.template,
                      {
                          'camera': Camera(),
                          'lidar': Lidar(),
                          'config': Config(),
                      })

    def post(self, request):
        if 'file' in request.FILES:
            data = request.FILES['file'].read()
            j = json.loads(data)
            models, msgs = self.load_from_json(j)

            return render(request, self.template,
                          {
                              'msgs': msgs,
                              'camera': models['cam'],
                              'lidar': models['lidar'],
                              'config': models['config']
                          })
        else:
            new_cam = CameraForm(request.POST)
            new_lidar = LidarForm(request.POST)
            if new_cam.is_valid():
                new_cam.save()
            if new_lidar.is_valid():
                new_lidar.save()
            return HttpResponse('saved')

    def load_from_json(self, data):
        cam = Camera()
        lidar = Lidar()
        config = Config()
        msgs = []
        if 'camera' in data:
            c_setting = data['camera']
            not_found = []
            try:
                cam.cname = c_setting['name']
            except:
                not_found.append('name')
            try:
                cam.width = c_setting['width']
            except:
                not_found.append('width')
            try:
                cam.height = c_setting['height']
            except:
                not_found.append('height')
            try:
                cam.mask = c_setting['mask']
            except:
                not_found.append('mask')
            try:
                cam.ctype = c_setting['type']
                if cam.ctype == 'perspective':
                    try:
                        cam.cfx = c_setting['k'][0][0]
                        cam.cfy = c_setting['k'][1][1]
                        cam.cx = c_setting['k'][0][2]
                        cam.cy = c_setting['k'][1][2]
                    except:
                        not_found += ['f', 'center of camera']
                    try:
                        # in case the dist is not in ideal shape
                        dist = np.zeros((5, ))
                        din = np.array(c_setting['dist']).reshape((-1, ))
                        i = 5 if din.shape[0] > 5 else din.shape[0]
                        dist[:i] = din
                        cam.ck1 = dist[0]
                        cam.ck2 = dist[1]
                        cam.cp1 = dist[2]
                        cam.cp2 = dist[3]
                        cam.ck3 = dist[4]
                    except:
                        not_found += ['distortion coefficient']
                if cam.ctype == 'fisheye' or cam.ctype == 'pinhole':
                    try:
                        cam.cx = c_setting['cx']
                    except:
                        not_found.append('cx')
                    try:
                        cam.cy = c_setting['cy']
                    except:
                        not_found.append('cy')
                    try:
                        cam.cfx, cam.cfy = c_setting['f'], c_setting['f']
                    except:
                        not_found.append('f')

                    if cam.ctype == 'pinhole':
                        try:
                            cam.fx *= c_setting['sx']
                        except:
                            pass
                        try:
                            cam.fy *= c_setting['sy']
                        except:
                            pass

                    if cam.ctype == 'fisheye':
                        try:
                            cam.ck1 = c_setting['k1']
                        except:
                            not_found.append('k1')
                        try:
                            cam.ck2 = c_setting['k2']
                        except:
                            not_found.append('k2')
                        try:
                            cam.cb1 = c_setting['b1']
                        except:
                            not_found.append('b1')
                        try:
                            cam.ck3 = c_setting['k3']
                        except:
                            not_found.append('k3')
            except:
                not_found.append('type')
            msgs += ['' if len(not_found) == 0 else f"camera: {', '.join(not_found)}"]
        else:
            msgs += ["camera information"]
        try:
            lidar.laser_num = data['frame']['laser_num']
            msgs += ['LiDAR: name']
        except:
            msgs += ['LiDAR: name, laser_num']
        return {'cam': cam, 'lidar': lidar, 'config': config}, msgs