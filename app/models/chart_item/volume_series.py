from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class VolumeSeries(pg.GraphicsObject):

    def __init__(self, data=None, color_bar="g", pen_color="b"):
        super(VolumeSeries, self).__init__()
        self._border_color = pen_color
        self._color_bar = color_bar
        self._data = data or []
        self._picture = None
        self.update_picture()

    def set_data(self, data):
        self._data = data

        range_limit = dict()
        max_high = max([item[0] for item in data]) if data else 1
        range_limit['xRange'] = [0, len(data)]
        range_limit['yRange'] = [0, max_high]
        self.getViewBox().setRange(**range_limit, padding=0.01)

        self.update_picture()

    def append(self, bar):
        self._data.append(bar)
        self.update_picture()

    def append_or_replace(self, bar):
        if len(self._data) == 0 or bar[1] not in [item[1] for item in self._data]:
            self._data.append(bar)
        else:
            index = next((index for (index, d) in enumerate(self._data) if d[1] == bar[1]), None)
            self._data[index] = bar
        self.update_picture()

    def update_picture(self):
        self._picture = QtGui.QPicture()
        pen = QtGui.QPainter(self._picture)
        pen.setPen(pg.mkPen(self._border_color))
        pen.setBrush(pg.mkBrush(self._color_bar))
        width = 1 / 3.
        for ind, bar in enumerate(self._data):
            pen.drawRect(QtCore.QRectF(ind - width, 0, width * 2, bar[0]))
        pen.end()
        self.update()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self._picture)

    def boundingRect(self):
        if self._data:
            x_min = np.float(-1)
            x_max = np.float(len(self._data) + 1)
            y_min = np.float(-1)
            y_max = np.float(max([v[0] for v in self._data]))
            return QtCore.QRectF(x_min, y_min, x_max-x_min, y_max-y_min)
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

        volumes = [item[0] for item in self._data[left:right]]
        minimum = 0
        maximum = max(volumes)

        return minimum, maximum

    def __len__(self):
        return len(self._data)
