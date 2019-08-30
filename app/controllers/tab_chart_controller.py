from aiohttp import ClientSession, WebSocketError, ClientConnectorError
from app.models import TickerTableModel, DepthTableModel
from stock_chart import StockPriceSeries
from PyQt5 import QtCore, QtWidgets
import asyncio
import json
import time


class TabChartController(QtCore.QObject):

    TICKER_TYPE = 'ticker'
    CANDLES_TYPE = 'candles'
    DEPTH_TYPE = 'depth'
    LISTING_TYPE = 'listing_info'

    WAITING_CONST = 'loading...'

    def __init__(self, view):
        super(TabChartController, self).__init__()
        self._view = view

        # disable UI while not get listing_info
        self._view.exchanges_combobox.setEnabled(False)
        self._view.pairs_combobox.setEnabled(False)
        self._view.timeframe_combobox.setEnabled(False)
        self._view.delete_ticker_button.setEnabled(False)

        # set models
        self._depth_model = DepthTableModel()
        self._view.depth_table.setModel(self._depth_model)
        self._tickers_model = TickerTableModel(['Pair', 'Bid', 'Ask'])
        self._view.tickers_table.setModel(self._tickers_model)

        # Information about access symbols and time_frames will get after send message to server
        self._view.exchanges_combobox.addItems([self.WAITING_CONST, ])
        self._view.exchanges_combobox.activated.connect(self._change_exchange_event)

        self._view.pairs_combobox.addItems([self.WAITING_CONST, ])
        self._view.pairs_combobox.activated.connect(self._select_new_symbol_event)

        # DoubleClick will start task chart-update and depth-update
        self._view.tickers_table.doubleClicked.connect(self._double_click_symbol_event)
        self._view.delete_ticker_button.pressed.connect(self._click_delete_symbol_button_event)

        self._view.autoscroll_checkbox.stateChanged.connect(self._state_change_scroll_check_box_event)
        self._view.autoscale_checkbox.stateChanged.connect(self._state_change_scaled_check_box_event)

        self._view.timeframe_combobox.activated.connect(self._change_time_frame_event)

        self._view.chart_type_combobox.activated.connect(self._change_type_chart_event)
        self._view.chart_type_combobox.addItems(['Candle', 'Bar', 'Line'])

        # save event loop link for start thread_save async methods
        self._loop = asyncio.new_event_loop()
        self._ws_manager = TabChartController.WSManager(self._loop)

        # ...connect slot to signal...
        self._ws_manager.update_ticker_signal.connect(self._update_ticker_slot)
        self._ws_manager.update_depth_signal.connect(self._update_depth_slot)
        self._ws_manager.update_candles_signal.connect(self._update_chart_slot)
        self._ws_manager.update_listing_signal.connect(self._update_listing_slot)
        self._ws_manager.show_error_signal.connect(self._print_error_slot)

        # ...and start
        self._ws_manager.start()

        # variables to track changes
        self._current_exchange = self._view.exchanges_combobox.itemText(0)

        self._chart_exchange = None
        self._chart_pair = None
        self._chart_time_frame = None

        # {exchange: [[time_frames], [pairs]], ...}
        self._listing_info = dict()

        # async task for listener ws
        self.tasks = dict()

        for i in range(0, 10):
            if not self._ws_manager.is_ws_connect:
                time.sleep(1)
            else:
                break
        else:
            QtWidgets.QMessageBox.critical(None, 'Error', 'Not connection to server')
            quit(-1)

        self._send_sub_message(data_id='listing_info')

    # Events
    def _state_change_scroll_check_box_event(self, state):
        self._view.price_chart.set_enable_auto_scroll(state)

    def _state_change_scaled_check_box_event(self, state):
        self._view.price_chart.set_enable_auto_scaled_oy(state)

    def _change_exchange_event(self, index):
        """Replace access pairs list or break if selected old exchange"""
        new_exchange = self._view.exchanges_combobox.itemText(index)

        if new_exchange not in self._listing_info.keys():
            return
        if self._current_exchange == new_exchange:
            return

        self._current_exchange = new_exchange
        self._view.pairs_combobox.clear()
        pairs = self._listing_info[self._current_exchange][1]  # {exchange: [[time_frames], [pairs]], ...}
        self._view.pairs_combobox.addItems([''] + pairs)

    def _change_time_frame_event(self, index):
        """If this new time frame, then unsub to old data and sub to new data"""
        new_time_frame = self._view.timeframe_combobox.itemText(index)
        if self._chart_time_frame == new_time_frame:
            return

        data_id = '.'.join([TabChartController.CANDLES_TYPE, self._chart_exchange,
                           self._chart_pair, self._chart_time_frame])
        self._send_unsub_message(data_id)

        self._chart_time_frame = new_time_frame
        self._view.price_chart.set_data([])
        self._view.volume_chart.set_data([])

        data_id = '.'.join([TabChartController.CANDLES_TYPE, self._chart_exchange, self._chart_pair,
                            self._chart_time_frame])
        self._send_sub_message(data_id)

    def _change_type_chart_event(self, index):
        type_chart = ''
        if index == 0:
            type_chart = StockPriceSeries.CANDLES_TYPE
        elif index == 1:
            type_chart = StockPriceSeries.BAR_TYPE
        elif index == 2:
            type_chart = StockPriceSeries.LINE_TYPE

        self._view.price_chart.change_type_chart(type_chart)

    def _select_new_symbol_event(self, index):
        """Subscribe to new pair ticker and add empty cells in table"""
        pair = self._view.pairs_combobox.itemText(index)

        if pair not in self._listing_info[self._current_exchange][1]:
            return
        if not pair or self._tickers_model.contain(f'{self._current_exchange} | {pair}'):
            return

        pair_and_exchange = self._current_exchange + ' | ' + pair
        self._view.pairs_combobox.setCurrentIndex(0)

        data_id = '.'.join([TabChartController.TICKER_TYPE, self._current_exchange, pair])
        self._send_sub_message(data_id)

        self._tickers_model.update([pair_and_exchange, '-', '-'])

    def _click_delete_symbol_button_event(self):
        """Unsub to ticker and check does it deleted pair pair at chart. if yes, then clear chart"""
        model = self._view.tickers_table.selectionModel()
        if not model.hasSelection():
            return

        indexes = model.selectedRows()
        # get first cell in selected row
        pair_and_exchange = self._view.tickers_table.model().index(indexes[0].row(), 0).data()
        exchange, pair = pair_and_exchange.split(' | ')
        data_id = '.'.join([TabChartController.TICKER_TYPE, exchange, pair])
        self._send_unsub_message(data_id)

        self._tickers_model.removeRow(indexes[0].row())
        self._view.tickers_table.selectionModel().clearSelection()

        if exchange == self._chart_exchange and pair == self._chart_pair:
            data_id = '.'.join([TabChartController.CANDLES_TYPE, self._chart_exchange, self._chart_pair,
                                self._chart_time_frame])
            self._send_unsub_message(data_id)

            data_id = '.'.join([TabChartController.DEPTH_TYPE, self._chart_exchange, self._chart_pair])
            self._send_unsub_message(data_id)

            self._clear_chart_info()

    def _double_click_symbol_event(self, index):
        """Select new symbol for show chart and depth"""
        exchange_and_pair = self._view.tickers_table.model().index(index.row(), 0).data()
        new_exchange, new_pair = exchange_and_pair.split(' | ')
        # if select pairs, that does it current pairs for chart, then return
        if self._chart_exchange == new_exchange and self._chart_pair == new_pair:
            return

        # if exist task, that listener chart and depth, then unsub
        if self._chart_exchange and self._chart_pair:
            data_id_chart = '.'.join([TabChartController.CANDLES_TYPE, self._chart_exchange, self._chart_pair,
                                      self._chart_time_frame])
            data_id_depth = '.'.join([TabChartController.DEPTH_TYPE, self._chart_exchange, self._chart_pair])
            self._chart_exchange, self._chart_pair, self._chart_time_frame = None, None, None
            self._send_unsub_message(data_id_chart)
            self._send_unsub_message(data_id_depth)

        self._clear_chart_info()

        self._view.timeframe_combobox.addItems(self._listing_info[new_exchange][0])
        time_frame = self._view.timeframe_combobox.currentText()
        self._view.price_chart.setTitle(f'{new_exchange} | {new_pair}')

        # sub at new data
        self._chart_exchange, self._chart_pair, self._chart_time_frame = new_exchange, new_pair, time_frame
        data_id = '.'.join([TabChartController.CANDLES_TYPE, new_exchange, new_pair, self._chart_time_frame])
        self._send_sub_message(data_id)
        data_id = '.'.join([TabChartController.DEPTH_TYPE, new_exchange, new_pair])
        self._send_sub_message(data_id)

    def _clear_chart_info(self):
        """Clear all UI and variables chart"""
        self._chart_pair = None
        self._chart_time_frame = None
        self._chart_exchange = None

        self._view.price_chart.set_data([])
        self._view.volume_chart.set_data([])
        self._depth_model.clear()
        self._view.price_chart.setTitle('')
        self._view.timeframe_combobox.clear()

    # Slots
    def _update_depth_slot(self, data):
        data_id = data['data_id']
        data_id_arr = data_id.split('.')
        exchange, pair = data_id_arr[2], data_id_arr[3]

        if self._chart_exchange == exchange and self._chart_pair == pair:
            self._depth_model.set_data(data['data'][0], data['data'][1])

    def _update_ticker_slot(self, data):
        data_id = data['data_id']
        data_id_arr = data_id.split('.')
        exchange, pair = data_id_arr[2], data_id_arr[3]

        if self._tickers_model.contain(f'{exchange} | {pair}'):
            data = (f'{exchange} | {pair}', data['data'][0], data['data'][1])
            self._tickers_model.update(data)

    def _update_chart_slot(self, data):
        data_id = data['data_id']
        data_id_arr = data_id.split('.')
        exchange, pair, time_frame = data_id_arr[2], data_id_arr[3], data_id_arr[4]

        if self._chart_exchange != exchange or self._chart_pair != pair or self._chart_time_frame != time_frame:
            return

        if data_id_arr[0] == 'update':
            ohlc = (float(data['data'][0]), float(data['data'][1]), float(data['data'][2]), float(data['data'][3]),
                    data['data'][5])
            volume = (float(data['data'][4]), data['data'][5])
            self._view.price_chart.append(ohlc)
            self._view.volume_chart.append(volume)
        elif data_id_arr[0] == 'starting':
            ohlc = [(float(item[0]), float(item[1]), float(item[2]), float(item[3]), item[5]) for item in data['data']]
            volume = [(float(item[4]), item[5]) for item in data['data']]
            self._view.price_chart.set_data(ohlc)
            self._view.volume_chart.set_data(volume)

    def _update_listing_slot(self, data):
        self._listing_info = data['data']

        self._view.exchanges_combobox.clear()
        self._view.exchanges_combobox.addItems(self._listing_info.keys())

        self._current_exchange = self._view.exchanges_combobox.currentText()
        self._view.pairs_combobox.clear()
        self._view.pairs_combobox.addItems(['', ] + self._listing_info[self._current_exchange][1])

        self._view.exchanges_combobox.setEnabled(True)
        self._view.pairs_combobox.setEnabled(True)
        self._view.timeframe_combobox.setEnabled(True)
        self._view.delete_ticker_button.setEnabled(True)

    def _print_error_slot(self, message):
        """Slot for show error message and delete UI item from error data_id"""
        QtWidgets.QMessageBox.critical(None, 'Error', f"Error at server {message['data_id']}: {message['error']}")

        if message['data_id'] == TabChartController.LISTING_TYPE:
            return

        fragment_id = message['data_id'].split('.')

        exchange, pair = fragment_id[2], fragment_id[3]
        if self._tickers_model.contain(f'{exchange} | {pair}'):
            self._tickers_model.removeRow(message['data_id'])

        if self._chart_exchange == exchange and self._chart_pair == pair:
            self._clear_chart_info()

    # WS
    def _send_sub_message(self, data_id):
        asyncio.run_coroutine_threadsafe(self._ws_manager.async_send_message(action='sub', data_id=data_id),
                                         self._loop)

    def _send_unsub_message(self, data_id):
        asyncio.run_coroutine_threadsafe(self._ws_manager.async_send_message(action='unsub', data_id=data_id),
                                         self._loop)

    class WSManager(QtCore.QThread):

        update_ticker_signal = QtCore.pyqtSignal(object)
        update_depth_signal = QtCore.pyqtSignal(object)
        update_candles_signal = QtCore.pyqtSignal(object)
        update_listing_signal = QtCore.pyqtSignal(object)
        show_error_signal = QtCore.pyqtSignal(object)

        IS_DEBUG = False

        ws_address = 'ws://localhost:8080/api/v1/ws'

        def __init__(self, loop):
            super().__init__()
            asyncio.set_event_loop(loop)
            self._loop = loop
            self.is_ws_connect = False
            self.ws = None

        def run(self):
            self._loop.create_task(self._async_start_consume())
            self._loop.run_forever()

        async def async_send_message(self, action, data_id):
            if not self.is_ws_connect:
                raise WebSocketError(code=-1, message='WS is not connection')

            await self.ws.send_json(
                dict(
                    action=action,
                    data_id=data_id
                )
            )

        async def _async_start_consume(self):
            try:
                async with ClientSession() as session:
                    async with session.ws_connect(self.ws_address) as self.ws:

                        self.is_ws_connect = True

                        while True:
                            response = await self.ws.receive()

                            if TabChartController.WSManager.IS_DEBUG:
                                print(response)

                            response = json.loads(response.data)

                            if 'error' in response.keys():
                                self.show_error_signal.emit(response)

                            if response['data_id'] == TabChartController.LISTING_TYPE:
                                response['data'] = json.loads(response['data'])

                            if response['data_id'] == TabChartController.LISTING_TYPE:
                                self.update_listing_signal.emit(response)
                            else:
                                data_type = response['data_id'].split('.')[1]
                                if data_type == TabChartController.TICKER_TYPE:
                                    self.update_ticker_signal.emit(response)
                                elif data_type == TabChartController.CANDLES_TYPE:
                                    self.update_candles_signal.emit(response)
                                elif data_type == TabChartController.DEPTH_TYPE:
                                    self.update_depth_signal.emit(response)
            except ClientConnectorError:
                pass
