from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class ChartTypeError(Exception):

    def __str__(self):
        return 'This chart type not exist'


class StockPriceSeries(pg.GraphicsObject):
    """Price series

    Storage data prices and logic for paint picture

    """

    CANDLES_TYPE = 'candles'
    BAR_TYPE = 'bar'
    LINE_TYPE = 'line'

    def __init__(self, data=None, chart_type=CANDLES_TYPE, border_color='b', positive_color='g',
                 negative_color='r', *args):
        """
        :param data: starting data in format: [open, high, low, close, time]
        :param chart_type: type chart (CANDLES_TYPE, BAR_TYPE, LINE_TYPE)
        :param border_color: color code for candles border or line chart
        :param positive_color: color code for up price
        :param negative_color: color code for down price
        """
        super(StockPriceSeries, self).__init__(*args)
        self._chart_type = chart_type
        self._border_color = border_color
        self._positive_color = positive_color
        self._negative_color = negative_color
        self._data = data or []
        self._picture = None
        self._generate_picture()

    def set_type_chart(self, chart_type):
        if chart_type not in (StockPriceSeries.CANDLES_TYPE, StockPriceSeries.BAR_TYPE, StockPriceSeries.LINE_TYPE):
            raise ChartTypeError()

        self._chart_type = chart_type
        self._generate_picture()

    def get_count(self):
        """return count price item

        :return: int

        """
        return len(self._data)

    def get_data(self):
        """return copy data array

        :return: [[open, high, low, close, time], ...]

        """
        return self._data[:]

    def set_data(self, data=None):
        """Set new data price"""
        self._data = data if data else []
        self._generate_picture()

    def append(self, data_price):
        """Append or replace price item

        append in end new data_point or replace old point
        if this price item with this 'time' contain in data array

        """
        times = [item[4] for item in self._data]
        if len(self._data) == 0 or data_price[4] not in times:
            self._data.append(data_price)
        else:
            index = next((index for (index, d) in enumerate(self._data) if d[4] == data_price[4]), None)
            self._data[index] = data_price
        self._generate_picture()

    def get_oy_min_and_max(self, to=None, do=None):
        to = to if to else 0
        do = do if do else self.get_count()

        if self._chart_type == StockPriceSeries.LINE_TYPE:
            seq_close = [item[3] for item in self._data[to:do]]
            minimum, maximum = (min(seq_close), max(seq_close)) if seq_close and seq_close else (None, None)
        else:
            seq_high = [item[1] for item in self._data[to:do]]
            seq_low = [item[2] for item in self._data[to:do]]
            minimum, maximum = (min(seq_low), max(seq_high)) if seq_low and seq_high else (None, None)

        return minimum, maximum

    def _generate_picture(self):
        """Paint picture (self._picture)"""

        self._picture = QtGui.QPicture()
        pen = QtGui.QPainter(self._picture)
        pen.setPen(pg.mkPen(self._border_color))

        if self._chart_type == self.CANDLES_TYPE:
            width = 1 / 3.
            for ind, candle in enumerate(self._data):
                # Warning. if paint line x->y | x==y, then at pyqtgraph will paint white rectangle
                if candle[1] != candle[2]:
                    # paint high->low
                    pen.drawLine(QtCore.QPointF(ind, candle[2]), QtCore.QPointF(ind, candle[1]))

                if candle[0] > candle[3]:
                    pen.setBrush(pg.mkBrush(self._negative_color))
                else:
                    pen.setBrush(pg.mkBrush(self._positive_color))

                pen.drawRect(QtCore.QRectF(ind - width, candle[0], width * 2, candle[3] - candle[0]))
        elif self._chart_type == self.BAR_TYPE:
            width = 1 / 3.
            for ind, candle in enumerate(self._data):
                if candle[0] > candle[3]:
                    pen.setPen(pg.mkPen(self._negative_color, width=5))
                else:
                    pen.setPen(pg.mkPen(self._positive_color, width=5))

                # Warning. if paint line x->y | x==y, then pyqtgraph will paint white rectangle (this error pyqtgraph?)
                if candle[1] != candle[2]:
                    pen.drawLine(QtCore.QPointF(ind, candle[2]), QtCore.QPointF(ind, candle[1]))

                pen.drawLine(QtCore.QPointF(ind - width, candle[0]), QtCore.QPointF(ind, candle[0]))
                pen.drawLine(QtCore.QPointF(ind, candle[3]), QtCore.QPointF(ind + width, candle[3]))
        elif self._chart_type == self.LINE_TYPE:
            for ind in range(0, len(self._data) - 1):
                pen.drawLine(QtCore.QPointF(ind, self._data[ind][3]),
                             QtCore.QPointF(ind + 1, self._data[ind + 1][3]))

        pen.end()
        self.update()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self._picture)

    def boundingRect(self):
        if self._data:
            prices = [(item[1], item[2], ind) for ind, item in enumerate(self._data)]
            numarr = np.array(prices)
            x_min = numarr[:, 2].min() - 1
            x_max = numarr[:, 2].max() + 1
            y_min = numarr[:, 1].min()
            y_max = numarr[:, 0].max()
            return QtCore.QRectF(x_min, y_min, x_max-x_min, y_max-y_min)
        return QtCore.QRectF(self._picture.boundingRect())
