import socket
import threading
import struct
import cv2
import numpy
import datetime

class Carame_Accept_Object:
    def __init__(self, S_addr_port=("", 8880)):
        self.resolution = (480, 360)
        self.img_fps = 15
        self.addr_port = S_addr_port
        self.Set_Socket(self.addr_port)

    def Set_Socket(self, S_addr_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(S_addr_port)
        self.server.listen(5)


def check_option(object, client):
    info = struct.unpack('lhh', client.recv(8))
    if info[0] > 888:
        object.img_fps = int(info[0]) - 888
        object.resolution = list(object.resolution)
        object.resolution[0] = info[1]
        object.resolution[1] = info[2]
        object.resolution = tuple(object.resolution)
        return 1
    else:
        return 0

def RT_Image(object, client, D_addr):
    avg = None
    if (check_option(object, client) == 0):
        return
    camera = cv2.VideoCapture(0) 
    img_param = [int(cv2.IMWRITE_JPEG_QUALITY), object.img_fps]  
    while (1):
        _, object.img = camera.read() 
        gray = cv2.cvtColor(object.img, cv2.COLOR_BGR2GRAY)  
        gray = cv2.GaussianBlur(gray, (21, 21), 0) 
        if avg is None:
            avg = gray.copy().astype("float")
            continue
        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        for c in contours:

            if cv2.contourArea(c) < 900:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(object.img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"
            cv2.putText(object.img, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(object.img, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                        (10, object.img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
           
        object.img = cv2.resize(object.img, object.resolution) 
        _, img_encode = cv2.imencode('.jpg', object.img, img_param) 
        img_code = numpy.array(img_encode)  
        object.img_data = img_code.tostring()  
        try:
           
            client.send(
                struct.pack("lhh", len(object.img_data), object.resolution[0], object.resolution[1]) + object.img_data)
        except:
            camera.release() 
            return


if __name__ == '__main__':
    camera = Carame_Accept_Object()
    while (1):
        client, D_addr = camera.server.accept()
        clientThread = threading.Thread(None, target=RT_Image, args=(camera, client, D_addr,))
        clientThread.start()
