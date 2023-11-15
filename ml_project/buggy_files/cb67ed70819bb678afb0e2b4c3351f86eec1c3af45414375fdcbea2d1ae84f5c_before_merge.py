    def execute_cmd(self, session=None, txt=None, **kwargs):
        """
        Take incoming data and send it to connected channel. This is
        triggered by the bot_data_in Inputfunc.

        Args:
            session (Session, optional): Session responsible for this
                command. Note that this is the bot.
            txt (str, optional):  Command string.
        Kwargs:
            user (str): The name of the user who sent the message.
            channel (str): The name of channel the message was sent to.
            type (str): Nature of message. Either 'msg', 'action', 'nicklist' or 'ping'.
            nicklist (list, optional): Set if `type='nicklist'`. This is a list of nicks returned by calling
                the `self.get_nicklist`. It must look for a list `self._nicklist_callers`
                which will contain all callers waiting for the nicklist.
            timings (float, optional): Set if `type='ping'`. This is the return (in seconds) of a
                ping request triggered with `self.ping`. The return must look for a list
                `self._ping_callers` which will contain all callers waiting for the ping return.

        """
        if kwargs["type"] == "nicklist":
            # the return of a nicklist request
            if hasattr(self, "_nicklist_callers") and self._nicklist_callers:
                chstr = "%s (%s:%s)" % (self.db.irc_channel, self.db.irc_network, self.db.irc_port)
                nicklist = ", ".join(sorted(kwargs["nicklist"], key=lambda n: n.lower()))
                for obj in self._nicklist_callers:
                    obj.msg("Nicks at %s:\n %s" % (chstr, nicklist))
                self._nicklist_callers = []
            return

        elif kwargs["type"] == "ping":
            # the return of a ping
            if hasattr(self, "_ping_callers") and self._ping_callers:
                chstr = "%s (%s:%s)" % (self.db.irc_channel, self.db.irc_network, self.db.irc_port)
                for obj in self._ping_callers:
                    obj.msg("IRC ping return from %s took %ss." % (chstr, kwargs["timing"]))
                self._ping_callers = []
            return

        elif kwargs["type"] == "privmsg":
            # A private message to the bot - a command.
            user = kwargs["user"]

            if txt.lower().startswith("who"):
                # return server WHO list (abbreviated for IRC)
                global _SESSIONS
                if not _SESSIONS:
                    from evennia.server.sessionhandler import SESSIONS as _SESSIONS
                whos = []
                t0 = time.time()
                for sess in _SESSIONS.get_sessions():
                    delta_cmd = t0 - sess.cmd_last_visible
                    delta_conn = t0 - session.conn_time
                    account = sess.get_account()
                    whos.append("%s (%s/%s)" % (utils.crop("|w%s|n" % account.name, width=25),
                                                utils.time_format(delta_conn, 0),
                                                utils.time_format(delta_cmd, 1)))
                text = "Who list (online/idle): %s" % ", ".join(sorted(whos, key=lambda w: w.lower()))
            elif txt.lower().startswith("about"):
                # some bot info
                text = "This is an Evennia IRC bot connecting from '%s'." % settings.SERVERNAME
            else:
                text = "I understand 'who' and 'about'."
            super(IRCBot, self).msg(privmsg=((text,), {"user": user}))
        else:
            # something to send to the main channel
            if kwargs["type"] == "action":
                # An action (irc pose)
                text = "%s@%s %s" % (kwargs["user"], kwargs["channel"], txt)
            else:
                # msg - A normal channel message
                text = "%s@%s: %s" % (kwargs["user"], kwargs["channel"], txt)

            if not self.ndb.ev_channel and self.db.ev_channel:
                # cache channel lookup
                self.ndb.ev_channel = self.db.ev_channel
            if self.ndb.ev_channel:
                self.ndb.ev_channel.msg(text, senders=self.id)