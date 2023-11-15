    def __del__(self):
        # remove textures from graphics card to prevent crash
        self.clearTextures()