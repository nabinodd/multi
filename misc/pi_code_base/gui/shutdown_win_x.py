import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

from gui_base.shutdown_win_base import Ui_Poweroff_ui

class Sdown_win_ui(qtw.QWidget):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,*kwargs)
        self.shutdown_win=Ui_Poweroff_ui()
        self.shutdown_win.setupUi(self)
        self.shutdown_win.cancel_btn.clicked.connect(self.close)

if __name__ == "__main__":
    app=qtw.QApplication([])

    main_win_widget=Sdown_win_ui()
    main_win_widget.show()
    app.exec()