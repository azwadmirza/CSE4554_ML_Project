    def __str__(self):
        "This handles what is shown when e.g. printing the message"
        senders = ",".join(getattr(obj, 'key', str(obj)) for obj in self.senders)
        
        receivers = ",".join(
            ["[%s]" % getattr(obj, 'key', str(obj)) for obj in self.channels] + [getattr(obj, 'key', str(obj)) for obj in self.receivers]
        )
        return "%s->%s: %s" % (senders, receivers, crop(self.message, width=40))