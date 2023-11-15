    def screenID(self):
        """Returns the screen ID or device context (depending on the platform)
        for the current Window
        """
        if sys.platform == 'win32':
            scrBytes = self.winHandle._dc
            if constants.PY3:
                _screenID = 0xFFFFFFFF & int.from_bytes(scrBytes, byteorder='little')
            else:
                _screenID = 0xFFFFFFFF & scrBytes
        elif sys.platform == 'darwin':
            try:
                _screenID = self.winHandle._screen.id  # pyglet1.2alpha1
            except AttributeError:
                _screenID = self.winHandle._screen._cg_display_id  # pyglet1.2
        elif sys.platform.startswith('linux'):
            _screenID = self.winHandle._x_screen_id
        return _screenID