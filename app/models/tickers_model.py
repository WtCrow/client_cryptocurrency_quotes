from PyQt5.QtCore import Qt
from PyQt5 import QtCore


class TickerTableModel(QtCore.QAbstractTableModel):
    """Model for ticker table"""

    def __init__(self, header, parent=None):
        super(TickerTableModel, self).__init__(parent)
        self._headers = header
        self._data = []

    def removeRow(self, row, parent=None):
        try:
            del self._data[row]
            self.layoutChanged.emit()
            return True
        except ValueError:
            return False

    def update(self, data):
        symbols = [item[0] for item in self._data]
        if data[0] in symbols:
            index = symbols.index(data[0])
            self._data[index] = data
        else:
            self._data.append(data)

        self.layoutChanged.emit()

    def contain(self, data):
        symbols = [item[0] for item in self._data]
        if data in symbols:
            return True
        return False

    def clear(self):
        self._data = []
        self.layoutChanged.emit()

    def rowCount(self, n):
        if not self._data:
            return 0
        return len(self._data)

    def columnCount(self, n):
        return len(self._headers)

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # почему то isdigit, isdecimal и т. д. не работают на очень малых числах, так что try except
            try:
                result = self._data[index.row()][index.column()]
            except ValueError:
                result = self._data[index.row()][index.column()]
            return result

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
