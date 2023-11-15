    def on_finished(self, reply, capture_errors):
        self.status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        request_queue.parse_queue()

        if not reply.isOpen() or not self.status_code:
            self.received_json.emit(None, reply.error())
            return

        data = reply.readAll()
        try:
            json_result = json.loads(str(data), encoding='latin_1')

            if 'error' in json_result and capture_errors and not self.window.core_manager.shutting_down:
                self.show_error(TriblerRequestManager.get_message_from_error(json_result))
            else:
                self.received_json.emit(json_result, reply.error())
        except ValueError:
            self.received_json.emit(None, reply.error())
            logging.error("No json object could be decoded from data: %s" % data)

        # We disconnect the slot since we want the finished only to be emitted once. This allows us to reuse the
        # request manager.
        try:
            reply.finished.disconnect()
            self.received_json.disconnect()
        except TypeError:
            pass  # We probably didn't have any connected slots.

        try:
            reply.deleteLater()
        except RuntimeError:
            pass

        self.reply = None