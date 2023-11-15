    def _showtraceback(self, etype, evalue, stb):

        exc_content = {
            u'traceback' : stb,
            u'ename' : unicode(etype.__name__),
            u'evalue' : unicode(evalue)
        }

        dh = self.displayhook
        # Send exception info over pub socket for other clients than the caller
        # to pick up
        exc_msg = dh.session.send(dh.pub_socket, u'pyerr', exc_content, dh.parent_header)

        # FIXME - Hack: store exception info in shell object.  Right now, the
        # caller is reading this info after the fact, we need to fix this logic
        # to remove this hack.  Even uglier, we need to store the error status
        # here, because in the main loop, the logic that sets it is being
        # skipped because runlines swallows the exceptions.
        exc_content[u'status'] = u'error'
        self._reply_content = exc_content
        # /FIXME
        
        return exc_content