    def find_user_dict(self):
        """Return the full path to the local dictionary."""
        c = self.c
        table = (
            c.config.getString('enchant-local-dictionary'),
                # Settings first.
            g.os_path_finalize_join(g.app.homeDir, '.leo', 'spellpyx.txt'),
                # #108: then the .leo directory.
            g.os_path_finalize_join(g.app.loadDir, "..", "plugins", 'spellpyx.txt'),
                # The plugins directory as a last resort.
        )
        for path in table:
            if g.os_path_exists(path):
                return path
        #
        g.es_print('Do spellpyx.txt file found')
        return None