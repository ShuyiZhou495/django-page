from channels.generic.websocket import  AsyncJsonWebsocketConsumer, WebsocketConsumer
import json
from calibration.funcs.main import run
import threading
import calibration.funcs.base.globals as variables
from asyncio import sleep
import ctypes

class CalibrationConsumer(AsyncJsonWebsocketConsumer):
    x = threading.Thread()
    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        print('trying to kill the thread')
        await self.state('exit', 'start', 'exiting...')
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.x.ident),
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.x.ident), 0)
            print('Exception raise failure')
        while self.x.is_alive():
            pass
        await self.state('exit', 'finish')
        await self.close()


    async def state(self, id, status, msg=''):
        await self.send(json.dumps({id: {status: msg}}))
        if status=='err':
            await self.close()

    async def cal_msg(self, event):
        await self.send_json({
            event['id']: {
                event['status']: event['msg']
            }
        })
        if(event['status']) == 'err':
            await self.close()

    async def connect(self):
        await self.channel_layer.group_add("cal", self.channel_name)
        await self.accept()
        print(self.scope['url_route']['kwargs']['config_id'])
        self.x = threading.Thread(target=run, args=(2, ))
        self.x.daemon = True
        self.x.start()


        #
        # myCalibration.run()