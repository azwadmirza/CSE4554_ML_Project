    def save_history(self):
        """Save history to a text file in user home directory"""
        try:
            open(self.LOG_PATH, 'w').write("\n".join( \
                    [to_text_string(self.combo.itemText(index))
                     for index in range(self.combo.count())] ))
        except (UnicodeDecodeError, EnvironmentError):
            pass