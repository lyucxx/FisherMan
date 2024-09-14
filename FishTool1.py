import cv2
import pyautogui
import numpy as np
import time
import random
import pyaudio

class BLEMouse:
    def __init__(self):

        self.isFishing = False
        self.clickState = False
        self.detectedFishingSound = False

        self.p = pyaudio.PyAudio()
        self.CHUNK = 512  # 每次读取的数据块大小
        self.FORMAT = pyaudio.paInt16  # 数据格式
        self.CHANNELS = 1  # 单声道
        self.RATE = 18000  # 采样率
        self.THRESHOLD = 30000  # 阈值1.5
        self.INPUT_DEVICE_INDEX = 0
        
        self.countFish = 0

    def windowPicProcess(self):
        # 获取整个屏幕的截图
        self.screenshot = pyautogui.screenshot()

        self.screenpic = cv2.cvtColor(np.array(self.screenshot), cv2.COLOR_RGB2BGR)
        self.grayscreenpic = cv2.cvtColor(self.screenpic,cv2.COLOR_RGB2GRAY)

        self.tempic = cv2.imread("FH.png")
        self.tempgray = cv2.cvtColor(self.tempic,cv2.COLOR_RGB2GRAY)
        self.result = cv2.matchTemplate(self.grayscreenpic,self.tempgray,cv2.TM_CCOEFF_NORMED)

        w, h = self.tempgray.shape[::-1]

        self.loc = np.where(self.result >= 0.55)
        if len(self.loc[0]) > 0:
            self.isFishing = True
            # print("fishing",end= '',flush=True)
        else:
            self.isFishing = False
            # print("not fishing",end= '',flush=True)
        for pt in zip(*self.loc[::-1]):
            cv2.rectangle(self.screenpic, pt, (pt[0] + w, pt[1] + h), (255,255,255), 2)
        #cv2.imshow("screenshot",self.screenpic)

        # cv2.namedWindow("Real-time Screen Capture", cv2.WINDOW_NORMAL)
        # cv2.imshow("Real-time Screen Capture", self.screenpic)

    # def get_audio_devices(self):
    #     devices = sd.query_devices()
    #     for i, device in enumerate(devices):
    #         print(f"Device {i}: {device['name']} (input: {device['max_input_channels']})")
    def listenFishing(self):
        stream = self.p.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,
                    frames_per_buffer=self.CHUNK,
                    input_device_index=self.INPUT_DEVICE_INDEX    
                    )     #  
        data = np.frombuffer(stream.read(self.CHUNK), dtype=np.int16)
        self.loudness = np.max(np.abs(data))
        # loudness = np.max(data)
        if self.loudness > self.THRESHOLD:
            self.detectedFishingSound = True
        else:
            self.detectedFishingSound = False

        # 打印响度
        #print(f"Loudness: {self.loudness:.4f}, Detected Sound: {self.detectedFishingSound}")
    def sendMouseEvent(self):
        
        if (self.loudness < 1200) or (self.loudness > 30000):
            self.randomTime1 = random.uniform(0.8, 2)
            self.randomTime2 = random.uniform(0.2, 0.8)
            self.randomTime3 = random.uniform(0.5, 1.5)
            if self.isFishing == False and self.detectedFishingSound == False:
                if not self.clickState:
                    # self.ser.write(self.clickData)
                    time.sleep(self.randomTime1)
                    pyautogui.click(button='middle')  
                    time.sleep(self.randomTime3)
                    self.clickState = True          

            if self.isFishing == True and self.detectedFishingSound == True:
                if not self.clickState:
                    # self.ser.write(self.clickData)
                    time.sleep(self.randomTime2)
                    pyautogui.click(button='middle') 
                    self.countFish = self.countFish + 1
                    time.sleep(self.randomTime3)
                    self.clickState = True
                    #print("clicked")
            else:
                self.clickState = False  # 重置标志，以便下次满足条件时可以再次发送
                # self.ser.write(0x00)       
        else:
            return
if  __name__ == '__main__':
    WPP = BLEMouse()
    #WPP.get_audio_devices()
    while True:
        WPP.windowPicProcess()
        WPP.listenFishing()
        print(f"\rFishing State={WPP.isFishing}  |bited={WPP.detectedFishingSound}  |clicked={WPP.clickState}  |fished={WPP.countFish}  |loudness={WPP.loudness:.4f}     ", end='', flush=True) 
        WPP.sendMouseEvent()

        # WPP.mouseMove()
        # if cv2.waitKey(1) & 0xFF == ord('Q'):#检查是否按下了 'q' 键来关闭窗口。
        #     cv2.destroyAllWindows()
        #     break
