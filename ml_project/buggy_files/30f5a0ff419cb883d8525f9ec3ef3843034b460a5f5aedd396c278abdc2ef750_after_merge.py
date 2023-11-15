    def shutdown(self, exitcode=0, exitmsg=None):
        '''
        If sub-classed, run any shutdown operations on this method.
        '''
        log.info('The salt syndic is shutting down..')
        msg = 'The salt syndic is shutdown. '
        if exitmsg is not None:
            exitmsg = msg + exitmsg
        else:
            exitmsg = msg.strip()
        super(Syndic, self).shutdown(exitcode, exitmsg)