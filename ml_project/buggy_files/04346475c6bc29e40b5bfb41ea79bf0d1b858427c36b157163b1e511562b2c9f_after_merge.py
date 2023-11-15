    def execute(self, request):
        """ Starts the producer to send the next request to
        consumer.write(Frame(request))
        """
        with self._transaction_lock:
            try:
                _logger.debug("Current transaction state - {}".format(
                    ModbusTransactionState.to_string(self.client.state))
                )
                retries = self.retries
                request.transaction_id = self.getNextTID()
                _logger.debug("Running transaction "
                              "{}".format(request.transaction_id))
                _buffer = hexlify_packets(self.client.framer._buffer)
                if _buffer:
                    _logger.debug("Clearing current Frame "
                                  ": - {}".format(_buffer))
                    self.client.framer.resetFrame()
                broadcast = (self.client.broadcast_enable
                             and request.unit_id == 0)
                if broadcast:
                    self._transact(request, None, broadcast=True)
                    response = b'Broadcast write sent - no response expected'
                else:
                    expected_response_length = None
                    if not isinstance(self.client.framer, ModbusSocketFramer):
                        if hasattr(request, "get_response_pdu_size"):
                            response_pdu_size = request.get_response_pdu_size()
                            if isinstance(self.client.framer, ModbusAsciiFramer):
                                response_pdu_size = response_pdu_size * 2
                            if response_pdu_size:
                                expected_response_length = self._calculate_response_length(response_pdu_size)
                    if request.unit_id in self._no_response_devices:
                        full = True
                    else:
                        full = False
                    c_str = str(self.client)
                    if "modbusudpclient" in c_str.lower().strip():
                        full = True
                        if not expected_response_length:
                            expected_response_length = Defaults.ReadSize
                    response, last_exception = self._transact(
                        request,
                        expected_response_length,
                        full=full,
                        broadcast=broadcast
                    )
                    if not response and (
                            request.unit_id not in self._no_response_devices):
                        self._no_response_devices.append(request.unit_id)
                    elif request.unit_id in self._no_response_devices and response:
                        self._no_response_devices.remove(request.unit_id)
                    if not response and self.retry_on_empty and retries:
                        while retries > 0:
                            if hasattr(self.client, "state"):
                                _logger.debug("RESETTING Transaction state to "
                                              "'IDLE' for retry")
                                self.client.state = ModbusTransactionState.IDLE
                            _logger.debug("Retry on empty - {}".format(retries))
                            response, last_exception = self._transact(
                                request,
                                expected_response_length
                            )
                            if not response:
                                retries -= 1
                                continue
                            # Remove entry
                            self._no_response_devices.remove(request.unit_id)
                            break
                    addTransaction = partial(self.addTransaction,
                                             tid=request.transaction_id)
                    self.client.framer.processIncomingPacket(response,
                                                             addTransaction,
                                                             request.unit_id)
                    response = self.getTransaction(request.transaction_id)
                    if not response:
                        if len(self.transactions):
                            response = self.getTransaction(tid=0)
                        else:
                            last_exception = last_exception or (
                                "No Response received from the remote unit"
                                "/Unable to decode response")
                            response = ModbusIOException(last_exception,
                                                         request.function_code)
                    if hasattr(self.client, "state"):
                        _logger.debug("Changing transaction state from "
                                      "'PROCESSING REPLY' to "
                                      "'TRANSACTION_COMPLETE'")
                        self.client.state = (
                            ModbusTransactionState.TRANSACTION_COMPLETE)
                return response
            except ModbusIOException as ex:
                # Handle decode errors in processIncomingPacket method
                _logger.exception(ex)
                self.client.state = ModbusTransactionState.TRANSACTION_COMPLETE
                return ex