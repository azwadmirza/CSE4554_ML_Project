    def canonical_name(self):
        for multiname, channels in iteritems(context.custom_multichannels):
            for channel in channels:
                if self.name == channel.name:
                    return multiname

        for that_name in context.custom_channels:
            if tokenized_startswith(self.name.split('/'), that_name.split('/')):
                return self.name

        if any(c.location == self.location
               for c in concatv((context.channel_alias,), context.migrated_channel_aliases)):
            return self.name

        # fall back to the equivalent of self.base_url
        # re-defining here because base_url for MultiChannel is None
        return "%s://%s/%s" % (self.scheme, self.location, self.name)