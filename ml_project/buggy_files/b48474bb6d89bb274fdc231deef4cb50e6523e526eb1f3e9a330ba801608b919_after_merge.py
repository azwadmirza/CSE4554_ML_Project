    def __del__(self):
        # remove textures from graphics card to prevent OpenGl memory leak
        try:
            self.clearTextures()
        except ModuleNotFoundError:
            pass  # has probably been garbage-collected already