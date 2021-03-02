import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc

from gui_base.shutdown_win_base import Ui_Poweroff_ui

class Main_win_ui(qtw.QMainWindow):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,*kwargs)
        self.shutdown_win=Ui_Poweroff_ui()
        self.shutdown_win.setupUi(self)


if __name__ == "__main__":
    app=qtw.QApplication([])

    main_win_widget=Main_win_ui()
    main_win_widget.show()
    app.exec()