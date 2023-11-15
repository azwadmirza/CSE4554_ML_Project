    def msg(self, text=None, **kwargs):
        """
        Takes text from connected channel (only).

        Args:
            text (str, optional): Incoming text from channel.

        Kwargs:
            options (dict): Options dict with the following allowed keys:
                - from_channel (str): dbid of a channel this text originated from.
                - from_obj (list): list of objects sending this text.

        """
        from_obj = kwargs.get("from_obj", None)
        options = kwargs.get("options", None) or {}
        if not self.ndb.ev_channel and self.db.ev_channel:
            # cache channel lookup
            self.ndb.ev_channel = self.db.ev_channel
        if "from_channel" in options and text and self.ndb.ev_channel.dbid == options["from_channel"]:
            if not from_obj or from_obj != [self]:
                super(IRCBot, self).msg(channel=text)