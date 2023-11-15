    def update(self, *args):
        self.cursor.execute(QU.update_artist, args)