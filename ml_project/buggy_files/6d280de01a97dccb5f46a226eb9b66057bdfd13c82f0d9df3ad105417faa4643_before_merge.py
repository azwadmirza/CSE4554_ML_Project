    def isFrameReady(self):
        ''' Check if we should continue decode logic

        This is meant to be used in a while loop in the decoding phase to let
        the decoder know that there is still data in the buffer.

        :returns: True if ready, False otherwise
        '''
        raise NotImplementedException(
            "Method not implemented by derived class")