    def draw(self):
        """Draw the text to the back buffer"""
        # Border width
        self.box.setLineWidth(self.pallette['lineWidth']) # Use 1 as base if border width is none
        #self.borderWidth = self.box.lineWidth
        # Border colour
        self.box.setLineColor(self.pallette['lineColor'], colorSpace='rgb')
        #self.borderColor = self.box.lineColor
        # Background
        self.box.setFillColor(self.pallette['fillColor'], colorSpace='rgb')
        #self.fillColor = self.box.fillColor

        if self._needVertexUpdate:
            #print("Updating vertices...")
            self._updateVertices()
        if self.fillColor is not None or self.borderColor is not None:
            self.box.draw()

        # self.boundingBox.draw()  # could draw for debug purposes
        gl.glPushMatrix()
        self.win.setScale('pix')

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.glFont.textureID)
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_DEPTH_TEST)

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)
        gl.glEnableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        gl.glVertexPointer(2, gl.GL_DOUBLE, 0, self.verticesPix.ctypes)
        gl.glColorPointer(4, gl.GL_DOUBLE, 0, self._colors.ctypes)
        gl.glTexCoordPointer(2, gl.GL_DOUBLE, 0, self._texcoords.ctypes)

        self.shader.bind()
        self.shader.setInt('texture', 0)
        self.shader.setFloat('pixel', [1.0 / 512, 1.0 / 512])
        nVerts = len(self._text)*4

        gl.glDrawArrays(gl.GL_QUADS, 0, nVerts)
        self.shader.unbind()

        # removed the colors and font texture
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)
        gl.glDisableClientState(gl.GL_TEXTURE_COORD_ARRAY)
        gl.glDisableVertexAttribArray(1)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        gl.glDisable(gl.GL_TEXTURE_2D)

        if self.hasFocus:  # draw caret line
            self.caret.draw()

        gl.glPopMatrix()