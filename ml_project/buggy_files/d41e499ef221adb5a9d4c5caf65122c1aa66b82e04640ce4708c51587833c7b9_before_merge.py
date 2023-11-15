    def shutdown(self, exitcode=0, exitmsg=None):
        '''
        If sub-classed, run any shutdown operations on this method.
        '''
        logger.info('The salt minion is shutting down..')
        if hasattr(self, 'minion'):
            self.minion.destroy()
        msg = 'The salt minion is shutdown. '
        if exitmsg is not None:
            exitmsg = msg + exitmsg
        else:
            exitmsg = msg.strip()
        super(Minion, self).shutdown(exitcode, exitmsg)