from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View, generic
from calibration.models import ConfigForm, CameraForm, LidarForm, Camera, Lidar, Config
import json
import numpy as np
import sys

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

    def return_os(self):
        if sys.platform=='darwin':
            return 'mac'
        if sys.platform == 'win32' or sys.platform=='cygwin':
            return 'win'
        if sys.platform == 'linux'
            return 'linux'
        return ''

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
            models['config'].name = str(request.FILES['file'])

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
        # load camera
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
                cam.mask = c_setting['mask_' + self.return_os()]
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
        # load lidar
        try:
            lidar.laser_num = data['frame']['laser_num']
            msgs += ['LiDAR: name']
        except:
            msgs += ['LiDAR: name, laser_num']

        method_not_found = {
            'frames': [],
            'methods': [],
            'initial guess': [],
            'output setting': [],
            'running setting': []
        }
        try:
            config.select_frame_by_hand = data['select_frame_by_hand']
            if data['select_frame_by_hand']:
                try:
                    config.selected = str(", ".join(data['selected']))
                except:
                    method_not_found['frames'].append('selected')
            else:
                try:
                    config.start_frame = data['start_frame']
                except:
                    method_not_found['frames'].append('start_frame')
                try:
                    config.end_frame = data['end_frame']
                except:
                    method_not_found['frames'].append('end_frame')
                try:
                    config.use_frame = data['use']
                except:
                    method_not_found['frames'].append('use')
        except:
            method_not_found['frames'].append('select_frame_by_hand')
        if 'method' in data:
            method = data['method']
            try:
                config.verbose = method['verbose']
            except:
                method_not_found['output setting'].append('verbose')
            try:
                config.vis = method['vis']
            except:
                method_not_found['output setting'].append('vis')
            if 'test' in method:
                try:
                    config.test_amount = method['test']['amount']
                    if config.test_amount > 0:
                        try:
                            config.R_range = abs(method['R_range'][0])
                        except:
                            method_not_found['running setting'].append("R_range")
                        try:
                            config.t_range = abs(method['t_range'][0])
                        except:
                            method_not_found['running setting'].append("t_range")
                except:
                    method_not_found['running setting'].append('all')
            else:
                method_not_found['running setting'].append('all')
            if 'edge' in method:
                try:
                    config.edge_use = method['edge']['use']
                    if config.edge_use:
                        try:
                            config.check_laser = method['edge']['check_laser']
                        except:
                            method_not_found['methods'].append('check_laser')
                        try:
                            config.edge_path = method['edge']['edge_img_' + self.return_os()]
                        except:
                            method_not_found['methods'].append('edge path')
                        try:
                            config.discontinuity = method['edge']['discontinuity'][0]
                        except:
                            method_not_found['methods'].append('discontinuity')
                except:
                    method_not_found['methods'].append('use edge or not')
            else:
                method_not_found['methods'].append('edge')
            if 'mi' in method:
                try:
                    config.mi_use = method['mi']['use']
                    if config.mi_use:
                        try:
                            config.show_distribution = method['mi']['show_distribution']
                        except:
                            method_not_found['methods'].append('show distribution')
                except:
                    method_not_found['methods'].append('use mi or not')
            else:
                method_not_found['methods'].append('mi')
        else:
            method_not_found['methods'].append('all')
            method_not_found['running setting'].append('all')
            method_not_found['output setting'].append('all')
        if 'frame' in data:
            frame = data['frame']
            if 'image' in frame:
                image = frame['image']
                try:
                    config.img_path = image['path_' + self.return_os()]
                except:
                    method_not_found['frames'].append('image path')
                try:
                    config.img_type = image['type']
                except:
                    method_not_found['frames'].append('image type')
            else:
                method_not_found['frames'].append('image files')
            if 'scan' in frame:
                scan = frame['scan']
                try:
                    config.scan_path = scan['path_' + self.return_os()]
                except:
                    method_not_found['frames'].append('scan path')
                try:
                    config.skip_line = scan['skip_line']
                except:
                    method_not_found['frames'].append('skip line')
                try:
                    config.rxyz = scan['rxyz']
                except:
                    method_not_found['frames'].append('rxyz')
                try:
                    config.delimiter = scan['delimiter']
                except:
                    method_not_found['frames'].append('delimiters')

        else:
            method_not_found['frames'].append('image and scan file settings')

        msgs.append('Calibration Method Setting' + str(method_not_found))
        return {'cam': cam, 'lidar': lidar, 'config': config}, msgs