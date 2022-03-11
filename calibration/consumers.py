from channels.generic.websocket import  AsyncJsonWebsocketConsumer, WebsocketConsumer
import json
from calibration.funcs.main import run
import threading
import  calibration.funcs.methods.edge as edge
import ctypes
import os, shutil
from calibration_methods.settings import MEDIA_ROOT

class CalibrationConsumer(AsyncJsonWebsocketConsumer):
    x = threading.Thread()

    async def kill(self):
        print('trying to kill the thread')
        await self.state('exit', 'start', 'exiting...')
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.x.ident),
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.x.ident), 0)
            print('Exception raise failure')
        while self.x.is_alive():
            pass

        for filename in os.listdir(MEDIA_ROOT):
            file_path = os.path.join(MEDIA_ROOT, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        await self.state('exit', 'finish')
        await self.close()

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        if text_data == 'kill':
            await self.kill()
        elif text_data == 'edge_pause':
            edge.Edge.pause_ = True
            await self.state('frame', 'msg', 'waiting to pause')

    async def state(self, id, status, msg=''):
        await self.send(json.dumps({id: {status: msg}}))
        if status=='err':
            await self.kill()

    async def cal_msg(self, event):
        if event['id'] == 'exit':
            await self.kill()
            return
        if event['status'] == 'img':
            print(type(event['msg']))
            await self.send(text_data=event['msg'])
        else:
            await self.send_json({
                event['id']: {
                    event['status']: event['msg']
                }
            })
        if event['status'] == 'err':
            await self.kill()

    async def connect(self):
        await self.channel_layer.group_add("cal", self.channel_name)
        await self.accept()
        print(self.scope['url_route']['kwargs']['config_id'])
        self.x = threading.Thread(target=run, args=(self.scope['url_route']['kwargs']['config_id'], ))
        self.x.daemon = True
        edge.Edge.pause_ = False
        self.x.start()


        #
        # myCalibration.run()