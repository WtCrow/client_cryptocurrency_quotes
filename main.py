if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    from app.views.general_ui import GeneralUI

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = GeneralUI(MainWindow)
    MainWindow.showMaximized()
    sys.exit(app.exec_())
