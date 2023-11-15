    def _layout(self):
        """Layout the text, calculating the vertex locations
        """
        def getLineWidthFromPix(pixVal):
            return pixVal / self._pixelScaling + self.padding * 2
        
        rgb = self._foreColor.rgba
        font = self.glFont

        # the vertices are initially pix (natural for freetype)
        # then we convert them to the requested units for self._vertices
        # then they are converted back during rendering using standard BaseStim
        vertices = np.zeros((len(self._layoutText) * 4, 2), dtype=np.float32)
        self._charIndices = np.zeros((len(self._layoutText)), dtype=int)
        self._colors = np.zeros((len(self._layoutText) * 4, 4), dtype=np.double)
        self._texcoords = np.zeros((len(self._layoutText) * 4, 2), dtype=np.double)
        self._glIndices = np.zeros((len(self._layoutText) * 4), dtype=int)

        # the following are used internally for layout
        self._lineNs = np.zeros(len(self._layoutText), dtype=int)
        self._lineTops = []  # just length of nLines
        self._lineBottoms = []
        self._lineLenChars = []  #
        self._lineWidths = []  # width in stim units of each line

        self._lineHeight = font.height * self.lineSpacing

        if np.isnan(self._requestedSize[0]):
            lineMax = float('inf')
        else:
            lineMax = (self._requestedSize[0] - self.padding) * self._pixelScaling

        current = [0, 0]
        fakeItalic = 0.0
        fakeBold = 0.0
        # for some reason glyphs too wide when using alpha channel only
        if font.atlas.format == 'alpha':
            alphaCorrection = 1 / 3.0
        else:
            alphaCorrection = 1

        wordLen = 0
        charsThisLine = 0
        wordsThisLine = 0
        lineN = 0

        for i, charcode in enumerate(self._layoutText):

            printable = True  # unless we decide otherwise
            # handle formatting codes
            if charcode in codes.values():
                if charcode == codes['ITAL_START']:
                    fakeItalic = 0.1 * font.size
                elif charcode == codes['ITAL_END']:
                    fakeItalic = 0.0
                elif charcode == codes['BOLD_START']:
                    fakeBold = 0.3 * font.size
                elif charcode == codes['BOLD_END']:
                    current[0] -= fakeBold / 2  # we expected bigger current
                    fakeBold = 0.0
                continue
            # handle newline
            if charcode == '\n':
                printable = False

            # handle printable characters
            if printable:
                if showWhiteSpace and charcode == " ":
                    glyph = font[u"·"]
                else:
                    glyph = font[charcode]
                xBotL = current[0] + glyph.offset[0] - fakeItalic - fakeBold / 2
                xTopL = current[0] + glyph.offset[0] - fakeBold / 2
                yTop = current[1] + glyph.offset[1]
                xBotR = xBotL + glyph.size[0] * alphaCorrection + fakeBold
                xTopR = xTopL + glyph.size[0] * alphaCorrection + fakeBold
                yBot = yTop - glyph.size[1]
                u0 = glyph.texcoords[0]
                v0 = glyph.texcoords[1]
                u1 = glyph.texcoords[2]
                v1 = glyph.texcoords[3]
            else:
                glyph = font[u"·"]
                x = current[0] + glyph.offset[0]
                yTop = current[1] + glyph.offset[1]
                yBot = yTop - glyph.size[1]
                xBotL = x
                xTopL = x
                xBotR = x
                xTopR = x
                u0 = glyph.texcoords[0]
                v0 = glyph.texcoords[1]
                u1 = glyph.texcoords[2]
                v1 = glyph.texcoords[3]

            index = i * 4
            theseVertices = [[xTopL, yTop], [xBotL, yBot],
                             [xBotR, yBot], [xTopR, yTop]]
            texcoords = [[u0, v0], [u0, v1],
                         [u1, v1], [u1, v0]]

            vertices[i * 4:i * 4 + 4] = theseVertices
            self._texcoords[i * 4:i * 4 + 4] = texcoords
            self._colors[i*4 : i*4+4, :4] = rgb
            self._lineNs[i] = lineN
            current[0] = current[0] + glyph.advance[0] + fakeBold / 2
            current[1] = current[1] + glyph.advance[1]

            # are we wrapping the line?
            if charcode == "\n":
                lineWPix = current[0]
                current[0] = 0
                current[1] -= self._lineHeight
                lineN += 1
                charsThisLine += 1
                self._lineLenChars.append(charsThisLine)
                self._lineWidths.append(getLineWidthFromPix(lineWPix))
                charsThisLine = 0
                wordsThisLine = 0
            elif charcode in wordBreaks:
                wordLen = 0
                charsThisLine += 1
                wordsThisLine += 1
            elif printable:
                wordLen += 1
                charsThisLine += 1

            # end line with auto-wrap on space
            if current[0] >= lineMax and wordLen > 0 and wordsThisLine:
                # move the current word to next line
                lineBreakPt = vertices[(i - wordLen + 1) * 4, 0]
                wordWidth = current[0] - lineBreakPt
                # shift all chars of the word left by wordStartX
                vertices[(i - wordLen + 1) * 4: (i + 1) * 4, 0] -= lineBreakPt
                vertices[(i - wordLen + 1) * 4: (i + 1) * 4, 1] -= self._lineHeight
                # update line values
                self._lineNs[i - wordLen + 1: i + 1] += 1
                self._lineLenChars.append(charsThisLine - wordLen)
                self._lineWidths.append(getLineWidthFromPix(lineBreakPt))
                lineN += 1
                # and set current to correct location
                current[0] = wordWidth
                current[1] -= self._lineHeight
                charsThisLine = wordLen

            # have we stored the top/bottom of this line yet
            if lineN + 1 > len(self._lineTops):
                self._lineBottoms.append(current[1] + font.descender)
                self._lineTops.append(current[1] + self._lineHeight
                                      + font.descender/2)

        # finally add length of this (unfinished) line
        self._lineWidths.append(getLineWidthFromPix(current[0]))
        self._lineLenChars.append(charsThisLine)

        # convert the vertices to stimulus units
        self._rawVerts = vertices / self._pixelScaling

        # thisW = current[0] - glyph.advance[0] + glyph.size[0] * alphaCorrection
        # calculate final self.size and tightBox
        if np.isnan(self._requestedSize[0]):
            self.size[0] = max(self._lineWidths) + self.padding*2
        if np.isnan(self._requestedSize[1]):
            self.size[1] = ((lineN + 1) * self._lineHeight / self._pixelScaling
                            + self.padding * 2)

        # if we had to add more glyphs to make possible then 
        if self.glFont._dirty:
            self.glFont.upload()
            self.glFont._dirty = False
        self._needVertexUpdate = True