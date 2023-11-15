    def prepare_privmsg(self, nick, cmd, message, mc=None):
        # should we encrypt?
        box, encrypt = self.get_encryption_box(cmd, nick)
        if encrypt:
            if not box:
                log.debug('error, dont have encryption box object for ' + nick +
                          ', dropping message')
                return
            message = encrypt_encode(message.encode('ascii'), box)

        #Anti-replay measure: append the message channel identifier
        #to the signature; this prevents cross-channel replay but NOT
        #same-channel replay (in case of snooper after dropped connection
        #on this channel).
        if nick in self.active_channels:
            hostid = self.active_channels[nick].hostid
        else:
            log.info("Failed to send message to: " + str(nick) + \
                          "; cannot find on any message channel.")
            return
        msg_to_be_signed = message + str(hostid)

        self.daemon.request_signed_message(nick, cmd, message, msg_to_be_signed,
                                           hostid)