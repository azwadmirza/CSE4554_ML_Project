    def write_message(self, message, binary=False, locked=True):
        ''' Override parent write_message with a version that acquires a
        write lock before writing.

        '''
        def write_message_unlocked():
            future = super(WSHandler, self).write_message(message, binary)
            # don't yield this future or we're blocking on ourselves!
            raise gen.Return(future)
        if locked:
            with (yield self.write_lock.acquire()):
                write_message_unlocked()
        else:
            write_message_unlocked()