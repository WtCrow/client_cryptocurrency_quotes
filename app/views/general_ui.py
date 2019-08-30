from app.views.tab_chart import TabChartView
from PyQt5 import QtCore, QtWidgets


class GeneralUI(object):

    def __init__(self, main_window):
        name_window = "Crypto currency"
        name_tab_1 = "Chart"

        # Generate UI
        main_window.resize(1280, 720)
        central_widget = QtWidgets.QWidget(main_window)

        # main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # base tab
        self.tab_widget = QtWidgets.QTabWidget()
        # chart tab
        self.tab_chart_view = TabChartView()
        self.tab_widget.addTab(self.tab_chart_view, '')

        main_layout.addWidget(self.tab_widget)
        main_window.setCentralWidget(central_widget)

        main_window.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", name_window, None, -1))
        self.tab_widget.setTabText(self.tab_widget.indexOf(
            self.tab_chart_view), QtWidgets.QApplication.translate("MainWindow", name_tab_1, None, -1))

        self.tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(main_window)
