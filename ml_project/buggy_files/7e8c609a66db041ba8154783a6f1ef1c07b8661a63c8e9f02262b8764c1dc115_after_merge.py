    def update(self, *args):
        if self.version_id < 74:
            self.cursor.execute(QU.update_artist74, args)
        else:
            # No field for backdrops in Kodi 19, so we need to omit that here
            args = args[:3] + args[4:]
            self.cursor.execute(QU.update_artist82, args)