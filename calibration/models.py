from django.db import models
from django.forms import ModelForm
from django.contrib import admin

CAM_TYPES = [
    ('omni', 'Omnidirectional'),
    ('perspective', 'Perspective'),
    ('pinhole', 'Pinhole'),
    ('fisheye', 'Fisheye')
]

VIS_TYPES = [
    ('mi-r', 'show points within a range, colored by reflectivity'),
    ('mi', 'show points within a range'),
    ('edge-e', 'show edge points on image of edges'),
    ('edge', 'show edge points')
]

INI_TYPES = [
    ('quaternion', 'quaternion'),
    ('euler', 'euler')
]

class Camera(models.Model):
    cname = models.CharField(max_length=100)
    ctype = models.CharField(max_length=15, choices=CAM_TYPES)
    height, width = models.IntegerField(), models.IntegerField()
    ck1, ck2, cp1, cp2, ck3 = models.FloatField(blank=True, null=True), \
                              models.FloatField(blank=True, null=True), \
                              models.FloatField(blank=True, null=True), \
                              models.FloatField(blank=True, null=True), \
                              models.FloatField(blank=True, null=True)
    cfx, cfy, cx, cy, cb1 = models.FloatField(blank=True, null=True),\
                            models.FloatField(blank=True, null=True), \
                            models.FloatField(blank=True, null=True), \
                            models.FloatField(blank=True, null=True), \
                            models.FloatField(blank=True, null=True)
    mask = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.cname + '-' + self.ctype

class Lidar(models.Model):
    lname = models.CharField(max_length=100)
    laser_num = models.IntegerField(default=0)

    def __str__(self):
        return self.lname

class Config(models.Model):

    name = models.CharField(max_length=100)
    # frame setting
    select_frame_by_hand = models.BooleanField(default=False)
    selected = models.CharField(max_length=100, blank=True, null=True)

    start_frame, end_frame = models.IntegerField(blank=True, null=True), models.IntegerField(blank=True, null=True)
    use_frame = models.IntegerField(blank=True, null=True)

    scan_path, img_path = models.CharField(max_length=200), models.CharField(max_length=200)
    img_type = models.CharField(max_length=20)
    skip_line = models.IntegerField(default=0)
    rxyz = models.BooleanField(default=False)
    delimiter = models.CharField(max_length=10)

    # output setting
    verbose = models.BooleanField(default=False)
    vis = models.CharField(max_length=20, choices=VIS_TYPES)

    # test
    test_amount = models.IntegerField(default=0)
    R_range = models.FloatField(blank=True, null=True)
    t_range = models.FloatField(blank=True, null=True)


    # camera & lidar
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    lidar = models.ForeignKey(Lidar, on_delete=models.CASCADE)

    # method mi
    mi_use = models.BooleanField(default=False)
    show_distribution = models.BooleanField(default=False)

    # method edge
    edge_use = models.BooleanField(default=False)
    check_laser = models.BooleanField(default=False)
    edge_path = models.CharField(max_length=200, blank=True, null=True)
    discontinuity = models.FloatField(blank=True, null=True)

    # initial guess
    ini_type = models.CharField(max_length=10, choices=INI_TYPES)
    degree = models.BooleanField(blank=True, null=True, default=False)
    R1, R2, R3, R4 = models.FloatField(default=0), models.FloatField(default=0), models.FloatField(default=0), \
                     models.FloatField(default=0, blank=True, null=True)
    t1, t2, t3 = models.FloatField(default=0), models.FloatField(default=0), models.FloatField(default=0)

class ConfigForm(ModelForm):
    class Meta:
        model = Config
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })


class CameraForm(ModelForm):
    class Meta:
        model = Camera
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super(CameraForm, self).__init__(*args, **kwargs)
    #     for field in self.fields.keys():
    #         self.fields[field].widget.attrs.update({
    #             'class':'form-control'
    #         })
    #


class LidarForm(ModelForm):
    class Meta:
        model = Lidar
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LidarForm, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].widget.attrs.update({
                'class':'form-control'
            })
