    def __str__(self):
        "This handles what is shown when e.g. printing the message"
        senders = ",".join(obj.key for obj in self.senders)
        receivers = ",".join(
            ["[%s]" % obj.key for obj in self.channels] + [obj.key for obj in self.receivers]
        )
        return "%s->%s: %s" % (senders, receivers, crop(self.message, width=40))