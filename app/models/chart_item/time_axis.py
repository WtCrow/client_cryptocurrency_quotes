import pyqtgraph as pg
import datetime


class CustomAxisItem(pg.AxisItem):
    """Custom axis for plot"""

    def __init__(self, data_axis=None, time_mask='%Y-%m-%d %H:%M', *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self._seq_data = data_axis if data_axis else []
        self._mask = time_mask

    def append(self, data_axis_list):
        if data_axis_list not in self._seq_data:
            self._seq_data.append(data_axis_list)

    def set_data(self, data_axis):
        self._seq_data = data_axis

    def tickStrings(self, values, scale, spacing):
        """Show axis item subject to scaling"""
        set_for_show = []
        for value in values:
            ind = int(value * scale)
            item = ''
            if 0 <= ind < len(self._seq_data):
                item = self._seq_data[ind]
                item = str(datetime.datetime.fromtimestamp(item).strftime(self._mask))
            set_for_show.append(item)
        return set_for_show

    def __len__(self):
        return len(self._data)
