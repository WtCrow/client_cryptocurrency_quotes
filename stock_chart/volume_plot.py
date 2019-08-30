from stock_chart.custom_axis import CustomAxisItem
from stock_chart.volume_series import VolumeSeries
from pyqtgraph import PlotWidget, ViewBox
from PyQt5 import QtCore


class VolumePlot(PlotWidget):
    """
    Столбиковый PlotWidget для объема.
    """

    def __init__(self, volumes=None, time_mask='', is_axis_x_show=True, *args, **kwargs):
        self._time_axis = None
        if is_axis_x_show:
            self._time_axis = CustomAxisItem(orientation='bottom')
            super(VolumePlot, self).__init__(axisItems={'bottom': self._time_axis}, *args, **kwargs)
            self.getPlotItem().showAxis('right')
            self.getPlotItem().getAxis('right').setStyle(showValues=True)
            self.time_mask = time_mask
        else:
            super(VolumePlot, self).__init__(*args, **kwargs)

        self._volume = VolumeSeries(volumes)
        self.getPlotItem().addItem(self._volume)

        # padding for show item on edge plot
        self._padding = .5
        self.setMenuEnabled(False)
        self.showGrid(True, True)

        # Set starting views range
        if self._volume.get_count() < 50:
            self.setXRange(0, 50)
        else:
            self.setXRange(self._volume.get_count() - 50, self._volume.get_count() + self._padding)

        # settings auto scaled
        self.getViewBox().disableAutoRange(ViewBox.XYAxes)
        self._timer_scaled = QtCore.QTimer()
        self._timer_scaled.timeout.connect(self._auto_scaled)
        self._timer_scaled.start()

    def append(self, volume):
        """Append new volume bar in format: [volume, time]"""
        self._volume.append(volume)
        if self._time_axis:
            self._time_axis.append(volume[1])

    def set_data(self, volumes):
        """set new volumes in format: [[volume, time], ...]"""
        self._volume.set_data(volumes)
        if self._time_axis:
            self._time_axis.set_data([item[1] for item in volumes])

    def _auto_scaled(self):
        """Find max volume and set limit [0-max_vol]"""
        view_range = self.getViewBox().viewRange()
        do = int(view_range[0][1])
        to = 0 if view_range[0][0] < 0 else int(view_range[0][0])

        data_volume = [item[0] for item in self._volume.get_data()[to:do]]
        max_y = max(data_volume) if data_volume else 10

        self.getViewBox().setRange(yRange=[0, max_y], padding=0)
