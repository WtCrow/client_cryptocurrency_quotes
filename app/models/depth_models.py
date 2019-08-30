from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt


class DepthTableModel(QtCore.QAbstractTableModel):
    """
    Модель данных стакана
    список предложений на продажу (красный фон) и на покупку (зеленый фон)
    rowCount определяет количество строк, которые следует пройти
    columnCount определяет количество колонок, которые следует пройти
    data определяет отображение данных
    headerData определяет отображение заголовков
    set_data установить новые данные
    clear отчистить таблицу
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
        self._source['buy'] = []
        self._source['sell'] = []
        self.layoutChanged.emit()

    def rowCount(self, n):
        # Вывод в таблицу идет единым списком, так что суммируем длины
        try:
            if not self._source:
                return 0
            return len(self._source['sell']) + len(self._source['buy'])
        except IndexError or KeyError:
            return 0

    def columnCount(self, n):
        return len(self._headers)

    def data(self, index, role):
        if not index:
            return False
        if role == Qt.DisplayRole:
            # пока есть элементы в sell, вставляем их
            if index.row() < len(self._source['sell']):
                return self._source['sell'][index.row()][index.column()]
            else:
                # sell закончился, получаем необходимый индекс в списке buy
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
