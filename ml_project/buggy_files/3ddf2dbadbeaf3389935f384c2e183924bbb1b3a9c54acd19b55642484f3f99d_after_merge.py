    def data_came_in(self, addr, data):
        """ The callback function that the thread pool will call when there is incoming data.
        :param addr: The (IP, port) address tuple of the sender.
        :param data: The data received.
        """
        if not self._is_running or not is_valid_address(addr):
            return

        ip, port = addr

        # decode the packet
        try:
            packet = decode_packet(data)
        except InvalidPacketException as e:
            self._logger.error(u"Invalid packet from [%s:%s], packet=[%s], error=%s", ip, port, hexlify(data), e)
            return

        if packet['opcode'] == OPCODE_WRQ:
            self._logger.error(u"WRQ is not supported from [%s:%s], packet=[%s]", ip, port, repr(packet))
            return

        self._logger.debug(u"GOT packet opcode[%s] from %s:%s", packet['opcode'], ip, port)
        # a new request
        if packet['opcode'] == OPCODE_RRQ:
            self._logger.debug(u"start handling new request: %s", packet)
            self._handle_new_request(ip, port, packet)
            return

        if (ip, port, packet['session_id']) not in self._session_dict:
            self._logger.warn(u"got non-existing session from %s:%s, id = %s", ip, port, packet['session_id'])
            return

        # handle the response
        session = self._session_dict[(ip, port, packet['session_id'])]
        self._process_packet(session, packet)

        if not session.is_done and not session.is_failed:
            return

        self._cleanup_session((ip, port, packet['session_id']))

        # schedule callback
        if session.is_failed:
            self._logger.info(u"%s failed", session)
            if session.failure_callback:
                callback = lambda cb = session.failure_callback, a = session.address, fn = session.file_name,\
                    msg = "download failed", ei = session.extra_info: cb(a, fn, msg, ei)
                self._callbacks.append(callback)
        elif session.is_done:
            self._logger.info(u"%s finished", session)
            if session.success_callback:
                callback = lambda cb = session.success_callback, a = session.address, fn = session.file_name,\
                    fd = session.file_data, ei = session.extra_info: cb(a, fn, fd, ei)
                self._callbacks.append(callback)

        self._schedule_callback_processing()