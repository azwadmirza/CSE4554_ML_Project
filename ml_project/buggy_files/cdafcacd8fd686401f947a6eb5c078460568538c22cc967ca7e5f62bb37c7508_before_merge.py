    def __del__(self):
        """Remove textures from graphics card to prevent crash
        """
        if not self.useShaders:
            GL.glDeleteLists(self._listID, 1)
        self.clearTextures()