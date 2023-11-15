    def vertices(self):
        textbox = self.textbox
        # check we have a caret index
        if self.index is None or self.index > len(textbox.text):
            self.index = len(textbox.text)
        if self.index < 0:
            self.index = 0
        # get the verts of character next to caret (chr is the next one so use
        # left edge unless last index then use the right of prev chr)
        # lastChar = [bottLeft, topLeft, **bottRight**, **topRight**]
        ii = self.index
        if textbox.vertices.shape[0] == 0:
            verts = textbox._getStartingVertices() / textbox._pixelScaling
            verts[:,1] = verts[:,1]
            verts[:,0] = verts[:,0] + float(textbox._anchorOffsetX)
        else:
            if self.index >= len(textbox._lineNs):  # caret is after last chr
                chrVerts = textbox.vertices[range((ii-1) * 4, (ii-1) * 4 + 4)]
                x = chrVerts[2, 0]  # x-coord of left edge (of final char)
            else:
                chrVerts = textbox.vertices[range(ii * 4, ii * 4 + 4)]
                x = chrVerts[1, 0]  # x-coord of right edge
            # the y locations are the top and bottom of this line
            y1 = textbox._lineBottoms[self.row] / textbox._pixelScaling
            y2 = textbox._lineTops[self.row] / textbox._pixelScaling
            # char x pos has been corrected for anchor already but lines haven't
            verts = (np.array([[x, y1], [x, y2]])
                     + (0, textbox._anchorOffsetY))

        return convertToPix(vertices=verts, pos=textbox.pos,
                            win=textbox.win, units=textbox.units)