from pyqtgraph import QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class VolumeSeries(pg.GraphicsObject):
    """Volume series

    Storage volume data and logic for paint picture

    """

    def __init__(self, data=None, color_bar="g", pen_color="b"):
        super(VolumeSeries, self).__init__()
        self._border_color = pen_color
        self._color_bar = color_bar
        self._data = data or []
        self._picture = None
        self._generate_picture()

    def get_count(self):
        """Return count volume points"""
        return len(self._data)

    def get_data(self):
        """Return copy volume data"""
        return self._data[:]

    def set_data(self, data):
        """Set new volume data"""
        self._data = data if data else []
        self._generate_picture()

    def append(self, bar):
        """Append or replace price item

        append in end new data_point or replace old point
        if this price item with this 'time' contain in data array
        format: [volume, time]

        """
        if len(self._data) == 0 or bar[1] not in [item[1] for item in self._data]:
            self._data.append(bar)
        else:
            index = next((index for (index, d) in enumerate(self._data) if d[1] == bar[1]), None)
            self._data[index] = bar
        self._generate_picture()

    def _generate_picture(self):
        """Создает изображение для отрисовки"""
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
        """
        Переопределенный метод отрисовки.
        Принимает QRectF как область для рисования
        """
        p.drawPicture(0, 0, self._picture)

    def boundingRect(self):
        """
        Переопределенный метод, определяет область отрисовки для метода paint
        Warning: если не использовать numpy, при сильном увеличении данные сотрутся.
        Т. о. очень малые значения видны не будут (пример: график пары HTMLBTC)
        """
        if self._data:
            volumes = [(item[0], ind) for ind, item in enumerate(self._data)]
            numarr = np.array(volumes)
            x_min = numarr[:, 1].min() - 1
            x_max = numarr[:, 1].max() + 1
            y_min = 0
            y_max = numarr[:, 0].max()
            return QtCore.QRectF(x_min, y_min, x_max-x_min, y_max-y_min)
        return QtCore.QRectF(self._picture.boundingRect())
