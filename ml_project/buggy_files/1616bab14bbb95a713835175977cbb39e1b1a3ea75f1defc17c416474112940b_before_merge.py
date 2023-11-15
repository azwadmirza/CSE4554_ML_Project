    def get_default_destination_dir(self):
        # set defaults downloads path
        value = self.config['download_defaults']['saveas']
        if not value:
            value = self.config['download_defaults']['saveas'] = str(get_default_dest_dir())
        return self.abspath(value)