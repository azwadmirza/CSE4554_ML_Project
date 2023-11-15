    def append_text_to_shell(self, text, error, prompt):
        """
        Append text to Python shell
        In a way, this method overrides the method 'insert_text' when text is 
        inserted at the end of the text widget for a Python shell
        
        Handles error messages and show blue underlined links
        Handles ANSI color sequences
        Handles ANSI FF sequence
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        if '\r' in text:    # replace \r\n with \n
            text = text.replace('\r\n', '\n')
            text = text.replace('\r', '\n')
        while True:
            index = text.find(chr(12))
            if index == -1:
                break
            text = text[index+1:]
            self.clear()
        if error:
            is_traceback = False
            for text in text.splitlines(True):
                if text.startswith('  File') \
                and not text.startswith('  File "<'):
                    is_traceback = True
                    # Show error links in blue underlined text
                    cursor.insertText('  ', self.default_style.format)
                    cursor.insertText(text[2:],
                                      self.traceback_link_style.format)
                else:
                    # Show error/warning messages in red
                    cursor.insertText(text, self.error_style.format)
            if is_traceback:
                self.traceback_available.emit(text)
        elif prompt:
            # Show prompt in green
            insert_text_to(cursor, text, self.prompt_style.format)
        else:
            # Show other outputs in black
            last_end = 0
            for match in self.COLOR_PATTERN.finditer(text):
                insert_text_to(cursor, text[last_end:match.start()],
                               self.default_style.format)
                last_end = match.end()
                try:
                    for code in [int(_c) for _c in match.group(1).split(';')]:
                        self.ansi_handler.set_code(code)
                except ValueError:
                    pass
                self.default_style.format = self.ansi_handler.get_format()
            insert_text_to(cursor, text[last_end:], self.default_style.format)
#            # Slower alternative:
#            segments = self.COLOR_PATTERN.split(text)
#            cursor.insertText(segments.pop(0), self.default_style.format)
#            if segments:
#                for ansi_tags, text in zip(segments[::2], segments[1::2]):
#                    for ansi_tag in ansi_tags.split(';'):
#                        self.ansi_handler.set_code(int(ansi_tag))
#                    self.default_style.format = self.ansi_handler.get_format()
#                    cursor.insertText(text, self.default_style.format)
        self.set_cursor_position('eof')
        self.setCurrentCharFormat(self.default_style.format)