from app.controllers.tab_chart_controller import TabChartController
from stock_chart import PriceStockPlot, VolumePlot
from PyQt5 import QtWidgets, Qt


class TabChartView(QtWidgets.QWidget):
    """
    Виджет с графиком, стаканом и обновляющимся списком символов
    """

    def __init__(self):
        super(TabChartView, self).__init__()
        self._setup_ui()
        self._controller = TabChartController(self)

    def _setup_ui(self):
        horizontal_layout = QtWidgets.QHBoxLayout(self)

        # list symbols area
        label_exchange = QtWidgets.QLabel('Exchanges')
        self.exchanges_combobox = QtWidgets.QComboBox()
        self.exchanges_combobox.setEditable(True)
        self.exchanges_combobox.setCurrentIndex(0)
        label_symbols = QtWidgets.QLabel('Pairs')
        self.pairs_combobox = QtWidgets.QComboBox()
        self.pairs_combobox.setEditable(True)
        self.tickers_table = QtWidgets.QTableView()
        self.tickers_table.setSelectionBehavior(Qt.QAbstractItemView.SelectRows)
        self.tickers_table.verticalHeader().close()
        self.tickers_table.setSelectionMode(Qt.QAbstractItemView.SingleSelection)
        self.delete_ticker_button = QtWidgets.QPushButton('Delete from list')

        vertical_layout_1 = QtWidgets.QVBoxLayout()
        vertical_layout_1.addWidget(label_exchange)
        vertical_layout_1.addWidget(self.exchanges_combobox)
        vertical_layout_1.addWidget(label_symbols)
        vertical_layout_1.addWidget(self.pairs_combobox)
        vertical_layout_1.addWidget(self.tickers_table)
        vertical_layout_1.addWidget(self.delete_ticker_button)
        horizontal_layout.addLayout(vertical_layout_1, 2)

        # table cup area
        self.depth_table = QtWidgets.QTableView()
        self.depth_table.setSelectionMode(Qt.QAbstractItemView.SelectionMode.NoSelection)
        self.depth_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.depth_table.verticalHeader().close()
        horizontal_layout.addWidget(self.depth_table, 2)

        # tools for chart area
        vertical_layout_2 = QtWidgets.QVBoxLayout()
        self.panel_layout = QtWidgets.QHBoxLayout()
        self.autoscroll_checkbox = QtWidgets.QCheckBox()
        self.autoscroll_checkbox.setChecked(True)
        self.autoscroll_checkbox.setText("Auto-scroll")
        self.panel_layout.addWidget(self.autoscroll_checkbox)
        self.autoscale_checkbox = QtWidgets.QCheckBox()
        self.autoscale_checkbox.setChecked(True)
        self.autoscale_checkbox.setText("Auto-scaled")
        self.panel_layout.addWidget(self.autoscale_checkbox)
        self.timeframe_combobox = QtWidgets.QComboBox()
        self.panel_layout.addWidget(self.timeframe_combobox)
        self.chart_type_combobox = QtWidgets.QComboBox()
        self.panel_layout.addWidget(self.chart_type_combobox)
        vertical_layout_2.addLayout(self.panel_layout, 1)

        # chart area
        self.price_chart = PriceStockPlot()
        self.price_chart.setBackground("w")
        self.price_chart.hideButtons()
        self.volume_chart = VolumePlot()
        self.volume_chart.setXLink(self.price_chart)
        self.volume_chart.setBackground("w")

        vertical_layout_2.addWidget(self.price_chart, 4)
        vertical_layout_2.addWidget(self.volume_chart, 1)
        horizontal_layout.addLayout(vertical_layout_2, 5)
