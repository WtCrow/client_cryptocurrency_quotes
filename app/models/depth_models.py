from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt


class DepthTableModel(QtCore.QAbstractTableModel):
    """Depth table model
    list asks prices. One row contain price sellers and quantity on this price. Red color.
    list bids prices. One row contain price buyers and quantity on this price. Green color.

    rowCount - count rows
    columnCount - count columns
    data - table for display.
        Format: [[buyers], [sellers]]. buyers | sellers : [[price, quantity], [price, quantity], ...]
    headerData - display settings
    set_data - set new data
    clear - clear all table
    """

    def __init__(self, parent=None):
        super(DepthTableModel, self).__init__(parent)
        self._headers = ['Price', 'Volume']
        self._source = dict(buy=[], sell=[])

    def set_data(self, buy, sell):
        self._source['buy'] = buy
        self._source['sell'] = sell
        self.layoutChanged.emit()

    def clear(self):
        self._source['buy'].clear()
        self._source['sell'].clear()
        self.layoutChanged.emit()

    def rowCount(self, n):
        if not self._source:
            return 0
        return len(self._source['sell']) + len(self._source['buy'])

    def columnCount(self, n):
        return len(self._headers)

    def data(self, index, role):
        if not index:
            return False
        if role == Qt.DisplayRole:
            # sell
            if index.row() < len(self._source['sell']):
                return self._source['sell'][index.row()][index.column()]
            else:
                # buy
                ind = index.row() - len(self._source['sell'])
                return self._source['buy'][ind][index.column()]
        elif role == Qt.BackgroundRole:
            if index.row() < len(self._source['sell']):
                return QtGui.QBrush(QtGui.QColor.fromRgb(QtGui.qRgb(255, 153, 153)))
            else:
                return QtGui.QBrush(QtGui.QColor.fromRgb(QtGui.qRgb(153, 255, 153)))

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]


if __name__ == '__main__':
    from PyQt5 import QtWidgets
    import sys

    app = QtWidgets.QApplication(sys.argv)
    tableView = QtWidgets.QTableView()

    tableView.verticalHeader().hide()
    m = DepthTableModel()
    source = ([['buy_price1', 'buy_volume1'], ['buy_price2', 'buy_volume2']],
              [['sell_price1', 'sell_volume1'], ['sell_price2', 'sell_volume2'], ['sell_price2', 'sell_volume2']])
    m.set_data(source[0], source[1])
    tableView.setModel(m)
    tableView.show()

    app.exec_()
