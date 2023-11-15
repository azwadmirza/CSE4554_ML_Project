    def sign_message(self, sequence, message, password):
        # Sign a message on device. Since we have big screen, of course we
        # have to show the message unabiguously there first!
        try:
            msg = message.encode('ascii', errors='strict')
            assert 1 <= len(msg) <= MSG_SIGNING_MAX_LENGTH
        except (UnicodeError, AssertionError):
            # there are other restrictions on message content,
            # but let the device enforce and report those
            self.handler.show_error('Only short (%d max) ASCII messages can be signed.' 
                                            % MSG_SIGNING_MAX_LENGTH)
            return b''

        path = self.get_derivation_prefix() + ("/%d/%d" % sequence)
        try:
            cl = self.get_client()
            try:
                self.handler.show_message("Signing message (using %s)..." % path)

                cl.sign_message_start(path, msg)

                while 1:
                    # How to kill some time, without locking UI?
                    time.sleep(0.250)

                    resp = cl.sign_message_poll()
                    if resp is not None:
                        break

            finally:
                self.handler.finished()

            assert len(resp) == 2
            addr, raw_sig = resp

            # already encoded in Bitcoin fashion, binary.
            assert 40 < len(raw_sig) <= 65

            return raw_sig

        except (CCUserRefused, CCBusyError) as exc:
            self.handler.show_error(str(exc))
        except CCProtoError as exc:
            self.logger.exception('Error showing address')
            self.handler.show_error('{}\n\n{}'.format(
                _('Error showing address') + ':', str(exc)))
        except Exception as e:
            self.give_error(e, True)

        # give empty bytes for error cases; it seems to clear the old signature box
        return b''