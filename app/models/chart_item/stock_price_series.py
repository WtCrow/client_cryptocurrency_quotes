from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class ChartTypeError(Exception):
    """Raise if set not access chart type"""

    def __str__(self):
        return 'This chart type not found, choose StockPriceSeries.CANDLES_TYPE, StockPriceSeries.BAR_TYPE, ' \
               'StockPriceSeries.LINE_TYPE'


class StockPriceSeries(pg.GraphicsObject):
    """
    Price series for finance chart.

    Storage data in format [[open, high, low, close, time], [...], ...].
        open, high, low, close - must float type
        time - can be str or unix-time
    Chart can by paint in 3 styles: candles (CANDLES_TYPE), bar (BAR_TYPE), line (LINE_TYPE)
    Auto-scaling will work by high and low if CANDLES_TYPE or BAR_TYPE used and by close if used LINE_TYPE.

    """

    CANDLES_TYPE = 'candles'
    BAR_TYPE = 'bar'
    LINE_TYPE = 'line'

    def __init__(self, data=None, chart_type=CANDLES_TYPE, border_color='b', positive_color='g', negative_color='r',
                 *args):
        """
        :param data: starting data in format [[open, high, low, close, time], [...], ...]
        :param chart_type: value from (CANDLES_TYPE, BAR_TYPE, LINE_TYPE) for get paint style
        :param border_color: color of shadow and candle border
        :param positive_color: color of up candle or bar
        :param negative_color: color of down candle or bar
        """
        super(StockPriceSeries, self).__init__(*args)
        self._data = data or []
        self._chart_type = chart_type
        self.border_color = border_color
        self.positive_color = positive_color
        self.negative_color = negative_color

        self._chart_paint_method = {StockPriceSeries.CANDLES_TYPE: self._get_candles_chart,
                                    StockPriceSeries.BAR_TYPE: self._get_bar_chart,
                                    StockPriceSeries.LINE_TYPE: self._get_line_chart}

        self._picture = None
        self.update_picture()

    def set_data(self, data):
        """Set new data set"""
        self._data = data

        range_limit = dict()
        max_high = max([item[1] for item in data]) if data else 1
        min_low = min([item[2] for item in data]) if data else 0
        range_limit['xRange'] = [0, len(data)]
        range_limit['yRange'] = [min_low, max_high]
        self.getViewBox().setRange(**range_limit, padding=0.01)

        self.update_picture()

    def append_or_replace(self, data_price):
        """
        Append new item or replace old price item by time.

        Append new data_point to end or replace old point.
        if 'time' already contain in data set, then replace.

        """
        index = -1
        for ind, candle in enumerate(self._data):
            if data_price[4] == candle[4]:
                index = ind
                break

        if len(self._data) == 0 or index == -1:
            self._data.append(data_price)
        else:
            self._data[index] = data_price
        self.update_picture()

    def append(self, data_price):
        """
        Append new item.

        Append new data_point to end.

        """
        self._data.append(data_price)
        self.update_picture()

    def set_chart_type(self, chart_type):
        """Set paint type for chart"""
        if chart_type not in self._chart_paint_method.keys():
            raise ChartTypeError()

        self._chart_type = chart_type
        self.update_picture()

    def _get_candles_chart(self):
        """Return QPicture() with candlestick chart by self._data"""
        picture = QtGui.QPicture()
        pen = QtGui.QPainter(picture)
        pen.setPen(pg.mkPen(self.border_color, width=2))
        width = 1 / 3.
        for ind, candle in enumerate(self._data):
            # Warning. if you paint line x -> y if x == y, then on pyqtgraph will paint white rectangle (bug?)
            if candle[1] != candle[2]:
                # paint shadow
                pen.drawLine(QtCore.QPointF(ind, candle[2]), QtCore.QPointF(ind, candle[1]))

            if candle[0] > candle[3]:
                pen.setBrush(pg.mkBrush(self.negative_color))
            else:
                pen.setBrush(pg.mkBrush(self.positive_color))
            # paint body
            pen.drawRect(QtCore.QRectF(ind - width, candle[0], width * 2, candle[3] - candle[0]))
        pen.end()
        return picture

    def _get_bar_chart(self):
        """Return QPicture() with bar chart by self._data"""
        picture = QtGui.QPicture()
        pen = QtGui.QPainter(picture)
        pen.setPen(pg.mkPen(self.border_color))
        width = 1 / 3.
        for ind, candle in enumerate(self._data):
            if candle[0] > candle[3]:
                pen.setPen(pg.mkPen(self.negative_color, width=5))
            else:
                pen.setPen(pg.mkPen(self.positive_color, width=5))
            # Warning. if paint line x->y | x==y, then pyqtgraph will paint white rectangle (bug?)
            if candle[1] != candle[2]:
                pen.drawLine(QtCore.QPointF(ind, candle[2]), QtCore.QPointF(ind, candle[1]))

            pen.drawLine(QtCore.QPointF(ind - width, candle[0]), QtCore.QPointF(ind, candle[0]))
            pen.drawLine(QtCore.QPointF(ind, candle[3]), QtCore.QPointF(ind + width, candle[3]))
        pen.end()
        return picture

    def _get_line_chart(self):
        """Return QPicture() with line chart by self._data"""
        picture = QtGui.QPicture()
        pen = QtGui.QPainter(picture)
        pen.setPen(pg.mkPen(self.border_color))
        for ind in range(0, len(self._data) - 1):
            pen.drawLine(QtCore.QPointF(ind, self._data[ind][3]), QtCore.QPointF(ind + 1, self._data[ind + 1][3]))
        pen.end()
        return picture

    def update_picture(self):
        """Update picture"""
        self._picture = self._chart_paint_method[self._chart_type]()
        self.update()

    def paint(self, p, *args):
        """overwrite for paint"""
        p.drawPicture(0, 0, self._picture)

    def boundingRect(self):
        # If not use numpy, then very small value will not paint
        if self._data:
            x_min = np.float(-1)
            x_max = np.float(len(self._data) + 1)
            y_min = np.float(-1)
            y_max = np.float(max([item[1] for item in self._data]))
            return QtCore.QRectF(x_min, y_min, x_max - x_min, y_max - y_min)
        return QtCore.QRectF(self._picture.boundingRect())

    def dataBounds(self, ax=None, frac=1.0, orthoRange=None):
        """For auto-scaling"""
        if not self._data:
            return None, None

        view_range = self.getViewBox().viewRange()
        count = len(self._data)
        # +-1 for extra indent
        left, right = int(view_range[0][0]) - 1, int(view_range[0][1]) + 1
        if (left < 0 and right < 0) or (left > count and right > count):
            return None, None
        if left < 0:
            left = 0

        if self._chart_type == StockPriceSeries.LINE_TYPE:
            seq_close = [item[3] for item in self._data[left:right]]
            minimum, maximum = min(seq_close), max(seq_close) if seq_close else (None, None)
        else:
            seq_high = [item[1] for item in self._data[left:right]]
            seq_low = [item[2] for item in self._data[left:right]]
            minimum, maximum = (min(seq_low), max(seq_high)) if seq_high and seq_low else (None, None)

        return minimum, maximum

    def __getitem__(self, item):
        return self._data[item]

    def __len__(self):
        return len(self._data)
