from django.urls import re_path
from .consumers import CalibrationConsumer

ws_urlpatterns = [
    re_path(r'^ws/calibration/(?P<config_id>\w+)$', CalibrationConsumer.as_asgi())
]