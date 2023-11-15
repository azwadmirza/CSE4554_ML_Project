    def is_local(self):
        # TODO: #1505  -- rethink this metaphor
        return int(self.w3.net.version) not in PUBLIC_CHAINS