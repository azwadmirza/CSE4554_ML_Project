    def addToFrame(self, message):
        ''' Add the next message to the frame buffer

        This should be used before the decoding while loop to add the received
        data to the buffer handle.

        :param message: The most recent packet
        '''
        raise NotImplementedException(
            "Method not implemented by derived class")