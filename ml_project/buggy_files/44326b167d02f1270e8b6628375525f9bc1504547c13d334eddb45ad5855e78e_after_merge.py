    def dataReceived(self, data):
        """
        Handle non-AMP messages, such as HTTP communication.
        """
        if data[0] == NUL:
            # an AMP communication
            if data[-2:] != NULNUL:
                # an incomplete AMP box means more batches are forthcoming.
                self.multibatches += 1
            try:
                super(AMPMultiConnectionProtocol, self).dataReceived(data)
            except KeyError:
                _LOGGER.trace("Discarded incoming partial data: {}".format(to_str(data)))
        elif self.multibatches:
            # invalid AMP, but we have a pending multi-batch that is not yet complete
            if data[-2:] == NULNUL:
                # end of existing multibatch
                self.multibatches = max(0, self.multibatches - 1)
            try:
                super(AMPMultiConnectionProtocol, self).dataReceived(data)
            except KeyError:
                _LOGGER.trace("Discarded incoming multi-batch data:".format(to_str(data)))
        else:
            # not an AMP communication, return warning
            self.transport.write(_HTTP_WARNING)
            self.transport.loseConnection()
            print("HTML received: %s" % data)