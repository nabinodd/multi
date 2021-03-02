from gui_base.main_win_base import Ui_Form
from gpiozero import CPUTemperature
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
from uptime import uptime

from shutdown_win_x import Sdown_win_ui

import threading
import datetime
import time
import os

class Main_win_ui(qtw.QMainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,*kwargs)
        self.m_win=Ui_Form()
 
        self.m_win.setupUi(self)
        self.m_win.dateEdit.setDate(qtc.QDate.currentDate())
        self.m_win.timeEdit.setTime(qtc.QTime.currentTime())
        self.m_win.module_val.setText('None')
        self.m_win.conn_sts_val.setText('N/A') ########Change this to get netw sts
 
        self.m_win.shutdown_btn.clicked.connect(self.open_shutdown)
        self.m_win.reboot_btn.clicked.connect(self.open_reboot)

        threading.Thread(target=self.update_data,daemon=True).start()
        self.resize(480,320)

    def open_shutdown(self):
        self.sdown_win=Sdown_win_ui()
        self.sdown_win.setWindowModality(qtc.Qt.ApplicationModal)
        self.sdown_win.shutdown_win.ok_btn.clicked.connect(self.shutdown_cmd)
        self.sdown_win.show()
        

    def open_reboot(self):
        self.sdown_win=Sdown_win_ui()
        self.sdown_win.setWindowModality(qtc.Qt.ApplicationModal)
        self.sdown_win.shutdown_win.ok_btn.clicked.connect(self.reboot_cmd)
        self.sdown_win.show()

    def showdialog(self,title,message):
        msg = qtw.QMessageBox()
        msg.setIcon(qtw.QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(qtw.QMessageBox.Ok)
        # msg.buttonClicked.connect(self.close)
        msg.exec_()


    def shutdown_cmd(self):
        pin_code=self.sdown_win.shutdown_win.pin_input.text()
        if pin_code=='2020':
            self.showdialog('Ok','Going to shutdown')
            os.system("shutdown now") 
        else:
            self.showdialog('Incorrect pin','Try again')

    def reboot_cmd(self):
        pin_code=self.sdown_win.shutdown_win.pin_input.text()
        if pin_code=='2020':
            self.showdialog('Ok','Going to reboot')
            os.system("shutdown now -r") 
        else:
            self.showdialog('Incorrect pin','Try again')

    def update_data(self):
        while True:
            cpu_temp = CPUTemperature()
            sys_uptime=int(uptime())
            up_time=datetime.timedelta(seconds=sys_uptime)
            self.m_win.bot_uptim_val.setText(str(up_time))
            self.m_win.cpu_temp_val.setText(str(cpu_temp.temperature))
            time.sleep(1)

if __name__ == "__main__":
    app=qtw.QApplication([])
    main_win_widget=Main_win_ui()
    main_win_widget.show()
    app.exec()