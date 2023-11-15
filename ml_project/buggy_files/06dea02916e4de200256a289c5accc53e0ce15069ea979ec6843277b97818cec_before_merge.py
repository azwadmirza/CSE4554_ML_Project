    def on_read_data(self):
        if self.receivers(self.finished) == 0:
            self.finished.connect(lambda reply: self.on_finished())
        self.connect_timer.stop()
        data = self.reply.readAll()
        self.current_event_string += data
        if len(self.current_event_string) > 0 and self.current_event_string[-1] == '\n':
            for event in self.current_event_string.split('\n'):
                if len(event) == 0:
                    continue
                json_dict = json.loads(str(event))

                received_events.insert(0, (json_dict, time.time()))
                if len(received_events) > 100:  # Only buffer the last 100 events
                    received_events.pop()

                if json_dict["type"] == "search_result_channel":
                    self.received_search_result_channel.emit(json_dict["event"]["result"])
                elif json_dict["type"] == "search_result_torrent":
                    self.received_search_result_torrent.emit(json_dict["event"]["result"])
                elif json_dict["type"] == "tribler_started" and not self.emitted_tribler_started:
                    self.tribler_started.emit()
                    self.emitted_tribler_started = True
                elif json_dict["type"] == "new_version_available":
                    self.new_version_available.emit(json_dict["event"]["version"])
                elif json_dict["type"] == "upgrader_started":
                    self.upgrader_started.emit()
                elif json_dict["type"] == "upgrader_finished":
                    self.upgrader_finished.emit()
                elif json_dict["type"] == "upgrader_tick":
                    self.upgrader_tick.emit(json_dict["event"]["text"])
                elif json_dict["type"] == "channel_discovered":
                    self.discovered_channel.emit(json_dict["event"])
                elif json_dict["type"] == "torrent_discovered":
                    self.discovered_torrent.emit(json_dict["event"])
                elif json_dict["type"] == "events_start":
                    self.events_started.emit(json_dict["event"])
                    self.tribler_version = json_dict["event"]["version"]
                    if json_dict["event"]["tribler_started"] and not self.emitted_tribler_started:
                        self.tribler_started.emit()
                        self.emitted_tribler_started = True
                elif json_dict["type"] == "torrent_finished":
                    self.torrent_finished.emit(json_dict["event"])
                elif json_dict["type"] == "market_ask":
                    self.received_market_ask.emit(json_dict["event"])
                elif json_dict["type"] == "market_bid":
                    self.received_market_bid.emit(json_dict["event"])
                elif json_dict["type"] == "market_ask_timeout":
                    self.expired_market_ask.emit(json_dict["event"])
                elif json_dict["type"] == "market_bid_timeout":
                    self.expired_market_bid.emit(json_dict["event"])
                elif json_dict["type"] == "market_transaction_complete":
                    self.market_transaction_complete.emit(json_dict["event"])
                elif json_dict["type"] == "market_payment_received":
                    self.market_payment_received.emit(json_dict["event"])
                elif json_dict["type"] == "market_payment_sent":
                    self.market_payment_sent.emit(json_dict["event"])
                elif json_dict["type"] == "market_iom_input_required":
                    self.market_iom_input_required.emit(json_dict["event"])
                elif json_dict["type"] == "signal_low_space":
                    self.low_storage_signal.emit(json_dict["event"])
                elif json_dict["type"] == "tribler_exception":
                    raise RuntimeError(json_dict["event"]["text"])
            self.current_event_string = ""