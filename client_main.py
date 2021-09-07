import sys
import socket
import cv2
import threading
import struct
import numpy
from PyQt5.QtGui import  *
from PyQt5.QtCore import  *
from PyQt5 import  QtWidgets
from PyQt5.QtWidgets import  (QLineEdit,QMessageBox,QFileDialog)

from design import Ui_MainWindow
from login  import Ui_Form

class MyLoginClass(QtWidgets.QMainWindow,Ui_Form):
   def __init__(self,parent=None):
       super(MyLoginClass,self).__init__(parent)
       self.setupUi(self)
       self.lg_Button.clicked.connect(self.end_event)# 绑定登陆函数
       self.ex_Button.clicked.connect(self.close)# 绑定退出函数
       self.setWindowTitle('登陆窗口')  # 窗口标题
       self.lineEdit_2.setEchoMode(QLineEdit.Password)  # 设置输入密码不可见
    # 登陆函数
   def end_event(self):
       if self.lineEdit.text() == "":
           QMessageBox.about(self, '提示', '请输入用户名')
       elif self.lineEdit_2.text() == "":
           QMessageBox.about(self, '提示', '请输入密码')
       elif self.lineEdit.text() == "mmz" and self.lineEdit_2.text() == "mmz":
           QMessageBox.about(self, '登陆成功', '欢迎使用本系统！')
           self.shop = MyMainClass()
           self.shop.show()
           self.close()
       else:
           QMessageBox.about(self, '提示', ' 用户名或密码输入错误！')

   def ex_Buttonclicked(self):
       print('exit')

class MyMainClass(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainClass, self).__init__(parent)
        self.setupUi(self)

        # 初始化定时器
        self.timer = QTimer(self)
        # 将定时器超时信号与槽函数showTime()连接
        self.timer.timeout.connect(self.showTime)
        # 设置计时间隔启动，每隔1000毫秒（1秒）发送一次超时信号，循环进行
        self.timer.start(1000)

        self.resolution = [480, 360]
        self.edt_IP.setText("172.20.10.4")
        self.edt_Port.setText("8880")
        #self.addr_port = ["172.20.10.4", 8880]
        self.src = 888 + 15  # 双方确定传输帧数，（888）为校验值
        self.interval = 0  # 图片播放时间间隔
        self.img_fps = 100  # 每秒传输多少帧数

        self.btn_con.clicked.connect(self.btn_con_clicked)
        self.btn_exit.clicked.connect(self.close)
    def showTime(self):
        # 获取系统现在的时间
        time = QDateTime.currentDateTime()
        # 设置系统时间显示格式
        timeDisplay = time.toString("yyyy-MM-dd hh:mm:ss dddd")
        # 在标签上显示时间
        self.label_time.setText(timeDisplay)

    def Set_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def Socket_Connect(self):
        self.Set_socket()
        self.client.connect(self.addr_port)
        print("IP is %s:%d" % (self.addr_port[0], self.addr_port[1]))

    def RT_Image(self):
        # 按照格式打包发送帧数和分辨率
        self.client.send(struct.pack("lhh", self.src, self.resolution[0], self.resolution[1]))
        while (1):
            info = struct.unpack("lhh", self.client.recv(8))
            buf_size = info[0]  # 获取读的图片总长度
            if buf_size:
                try:
                    self.buf = b""  # 代表bytes类型
                    #temp_buf = self.buf
                    while (buf_size):  # 读取每一张图片的长度
                        temp_buf = self.client.recv(buf_size)
                        buf_size -= len(temp_buf)
                        self.buf += temp_buf  # 获取图片
                        data = numpy.frombuffer(self.buf, dtype='uint8')  # 按uint8转换为图像矩阵
                        self.image = cv2.imdecode(data, 1)  # 图像解码
                        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                        #cv2.imshow("clientPort", self.image)  # 展示图片

                        height, width, bytesPerComponent = self.image.shape
                        bytesPerLine = bytesPerComponent * width
                        q_image = QImage(self.image.data, width, height, bytesPerLine,
                                         QImage.Format_RGB888).scaled(self.label_video.width(), self.label_video.height())
                        self.label_video.setPixmap(QPixmap.fromImage(q_image))
                except:
                    pass;
                finally:
                    if (cv2.waitKey(10) == 27):  # 每10ms刷新一次图片，按‘ESC’（27）退出
                        self.client.close()
                        cv2.destroyAllWindows()
                        break

    def button1_clicked(self):
        # 获取系统现在的时间
        filename = QDateTime.currentDateTime()
        # 设置系统时间显示格式
        filename1 = filename.toString("yyyyMMddhhmmss")
        filename2 = filename1 + '.jpg'
        cv2.imwrite(filename2, self.image)  # 保存图片
        openJpg = QPixmap(filename2).scaled(self.label.width(), self.label.height())
        self.label2.setPixmap(openJpg)
        self.label2.setScaledContents(True)  # 让图片自适应label大小

    def btn_con_clicked(self):

        IP = self.edt_IP.text()
        Port = self.edt_Port.text()
        Port = int(Port)
        self.addr_port = [IP, Port]
        self.addr_port = tuple(self.addr_port)#类型转换
        self.Socket_Connect()
        self.Get_Data(self.interval)
    #def button2_clicked(self):
    #    imgName, imgType = QFileDialog.getOpenFileName(self, "打开图片", "", "*.jpg")
    #    openJpg = QPixmap(imgName).scaled(self.label.width(), self.label.height())
    #    self.label2.setPixmap(openJpg)
    #    self.label2.setScaledContents(True)  # 让图片自适应label大小



    def Get_Data(self, interval):
        showThread = threading.Thread(target=self.RT_Image)
        showThread.start()


if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    ui=MyLoginClass()
    ui.show()
    sys.exit(app.exec_())