    def write_message(self, message, binary=False, locked=True):
        ''' Override parent write_message with a version that acquires a
        write lock before writing.

        '''
        if locked:
            with (yield self.write_lock.acquire()):
                yield super(WSHandler, self).write_message(message, binary)
        else:
            yield super(WSHandler, self).write_message(message, binary)