from django.contrib import admin

from .models import Camera, Lidar, Config

class CameraAdmin(admin.ModelAdmin):
    list_display = ('cname', 'ctype', 'height', 'width', 'mask')
    fieldsets = [
        (None, {'fields': ['cname', 'ctype', 'height', 'width', 'mask']}),
        ('parameters', {'fields': ['cfx', 'cfy', 'cx', 'cy', 'ck1', 'ck2', 'ck3', 'cp1', 'cp2','cb1']}),
    ]

admin.site.register(Camera, CameraAdmin)

class LidarAdmin(admin.ModelAdmin):
    list_display = ('lname', 'laser_num')

admin.site.register(Lidar, LidarAdmin)

class ConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'mi_use', 'edge_use')
    fieldsets = [
        (None, {'fields': ['name']}),
        ('camera & lidar', {'fields': ['camera', 'lidar']}),
        ('frame setting', {'fields': ['select_frame_by_hand', 'selected', 'start_frame', 'end_frame',
                                      'use_frame', 'scan_path', 'img_path', 'img_type',
                                      'skip_line', 'rxyz', 'delimiter']}),
        ('output setting', {'fields': ['verbose', 'vis']}),
        ('initial guess', {'fields': ['ini_type', 'degree', 'R1', 'R2', 'R3', 'R4', 't1', 't2', 't3']}),
        ('test setting', {'fields': ['test_amount', 'R_range', 't_range']}),
        ('method mutual information setting', {'fields':['mi_use', 'show_distribution']}),
        ('method edge setting', {'fields': ['edge_use', 'check_laser', 'edge_path', 'discontinuity']}),
    ]

admin.site.register(Config, ConfigAdmin)