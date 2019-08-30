from stock_chart.stock_price_series import StockPriceSeries
from stock_chart.custom_axis import CustomAxisItem
from pyqtgraph import PlotWidget, ViewBox
from PyQt5 import QtCore


class PriceStockPlot(PlotWidget):
    """Plot for paint StockPriceItem

    Paint, scaling and scroll to right edge price chart

    """

    def __init__(self, data=None, is_axis_x_show=False, *args, **kwargs):
        """
        :param data: starting data
        :param is_axis_x_show: show axis or hight
        """
        self._time_axis = None
        if is_axis_x_show:
            self._time_axis = CustomAxisItem(orientation='bottom')
            super(PriceStockPlot, self).__init__(axisItems={'bottom': self._time_axis}, *args, **kwargs)
        else:
            super(PriceStockPlot, self).__init__(*args, **kwargs)

        self._prices = StockPriceSeries(data)
        self.getPlotItem().addItem(self._prices)

        # padding for show price item at edge
        self._padding = .5
        self.getViewBox().setLimits(xMin=-self._padding)
        self._update_ox_max()

        # settings auto scaled
        self.getViewBox().disableAutoRange(ViewBox.XYAxes)
        self.is_auto_scaled_oy = True
        self._timer_scaled = QtCore.QTimer()
        self._timer_scaled.timeout.connect(self._auto_scaled_oy)
        self.set_enable_auto_scaled_oy(True)

        self.is_auto_scroll = True

        self.setMenuEnabled(False)
        self.showGrid(True, True)
        self.getPlotItem().showAxis('right')
        self.getPlotItem().getAxis('bottom').setStyle(showValues=is_axis_x_show)

        # Show 0-50 views range if count prices < 50, else show 50 last prices point
        if self._prices.get_count() < 50:
            self.setXRange(0, 50)
        else:
            self.setXRange(self._prices.get_count() - 50, self._prices.get_count() + self._padding)

    def append(self, price):
        """Add new price point in format [open, high, low, close, time]"""
        self._prices.append(price)
        if self._time_axis:
            self._time_axis.append(price[4])

        self._update_ox_max()
        if self.is_auto_scroll and price:
            self._scroll()

    def set_enable_auto_scroll(self, is_enable=True):
        """Scroll to right"""
        self.is_auto_scroll = is_enable

    def set_enable_auto_scaled_oy(self, is_enable=True):
        """Auto scaled"""
        self.is_auto_scaled_oy = is_enable

        # start or stop thread
        if self.is_auto_scaled_oy:
            self._timer_scaled.start()
        else:
            self._timer_scaled.stop()

    def set_data(self, prices):
        """Set new data"""
        self._prices.set_data(prices)
        if self._time_axis:
            self._time_axis.set_data([item[4] for item in prices])

        self._update_ox_max()
        if prices and self.is_auto_scroll:
            self._scroll()

    def change_type_chart(self, type_chart):
        self._prices.set_type_chart(type_chart)

    def _scroll(self):
        vb = self.getViewBox()
        view_range = vb.viewRange()

        # Get x coord left edge views area
        to_x = self._prices.get_count() - (view_range[0][1] - view_range[0][0])
        if to_x < -self._padding:
            to_x = -self._padding

        # Get x coord right edge views area
        do_x = self._prices.get_count()

        # Get y coord. Last close price show to center chart
        last_close_price = self._prices.get_data()[-1][3]
        len_y_view_range = view_range[1][1] - view_range[1][0]
        to_y = last_close_price - len_y_view_range // 2
        do_y = last_close_price + len_y_view_range // 2

        vb.setRange(xRange=[to_x, do_x], padding=0)
        if not self.is_auto_scaled_oy:
            vb.setRange(yRange=[to_y, do_y], padding=0)

    def _auto_scaled_oy(self):
        view_range = self.getViewBox().viewRange()
        to = 0 if view_range[0][0] < 0 else int(view_range[0][0])
        do = self._prices.get_count() if view_range[0][1] > self._prices.get_count() else int(view_range[0][1])
        minimum, maximum = self._prices.get_oy_min_and_max(to, do)

        if minimum and maximum:
            if minimum != maximum:
                self.getViewBox().setYRange(minimum, maximum)
            else:
                self.getViewBox().setYRange(minimum - minimum * .01, maximum + maximum * .01)

    def _update_ox_max(self):
        """Update limit OX"""
        if self._prices.get_count() < 50:
            self.getViewBox().setLimits(xMax=50 + self._padding)
        else:
            self.getViewBox().setLimits(xMax=self._prices.get_count() + self._padding)
