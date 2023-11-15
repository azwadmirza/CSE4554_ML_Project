    def save_history(self):
        """Save history to a text file in user home directory"""
        # Don't fail when saving search history to disk
        # See issues 8878 and 6864
        try:
            search_history = [to_text_string(self.combo.itemText(index))
                              for index in range(self.combo.count())]
            search_history = '\n'.join(search_history)
            open(self.LOG_PATH, 'w').write(search_history)
        except (UnicodeEncodeError, UnicodeDecodeError, EnvironmentError):
            pass