    def request_chunk(self, interface, index):
        if index in self.requested_chunks:
            return
        interface.print_error("requesting chunk %d" % index)
        self.requested_chunks.add(index)
        self.queue_request('blockchain.block.get_chunk', [index], interface)