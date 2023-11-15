    def on_message(self, fragment):
        ''' Process an individual wire protocol fragment.

        The websocket RFC specifies opcodes for distinguishing text frames
        from binary frames. Tornado passes us either a text or binary string
        depending on that opcode, we have to look at the type of the fragment
        to see what we got.

        Args:
            fragment (unicode or bytes) : wire fragment to process

        '''

        # We shouldn't throw exceptions from on_message because the caller is
        # just Tornado and it doesn't know what to do with them other than
        # report them as an unhandled Future

        try:
            message = yield self._receive(fragment)
        except Exception as e:
            # If you go look at self._receive, it's catching the
            # expected error types... here we have something weird.
            log.error("Unhandled exception receiving a message: %r: %r", e, fragment, exc_info=True)
            self._internal_error("server failed to parse a message")

        try:
            if message:
                work = yield self._handle(message)
                if work:
                    yield self._schedule(work)
        except Exception as e:
            log.error("Handler or its work threw an exception: %r: %r", e, message, exc_info=True)
            self._internal_error("server failed to handle a message")

        raise gen.Return(None)