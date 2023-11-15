    def _onCursorKeys(self, key):
        """Called by the window when cursor/del/backspace... are received"""
        if key == 'MOTION_UP':
            self.caret.row -= 1
        elif key == 'MOTION_DOWN':
            self.caret.row += 1
        elif key == 'MOTION_RIGHT':
            self.caret.char += 1
        elif key == 'MOTION_LEFT':
            self.caret.char -= 1
        elif key == 'MOTION_BACKSPACE':
            self.text = self.text[:self.caret.index-1] + self.text[self.caret.index:]
            self.caret.index -= 1
        elif key == 'MOTION_DELETE':
            self.text = self.text[:self.caret.index] + self.text[self.caret.index+1:]
        elif key == 'MOTION_NEXT_WORD':
            pass
        elif key == 'MOTION_PREVIOUS_WORD':
            pass
        elif key == 'MOTION_BEGINNING_OF_LINE':
            self.caret.char = 0
        elif key == 'MOTION_END_OF_LINE':
            self.caret.char = END_OF_THIS_LINE
        elif key == 'MOTION_NEXT_PAGE':
            pass
        elif key == 'MOTION_PREVIOUS_PAGE':
            pass
        elif key == 'MOTION_BEGINNING_OF_FILE':
            pass
        elif key == 'MOTION_END_OF_FILE':
            pass
        else:
            print("Received unhandled cursor motion type: ", key)