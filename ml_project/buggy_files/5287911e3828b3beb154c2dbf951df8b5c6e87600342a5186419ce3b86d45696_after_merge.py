    def refresh(self):
        """Update the source tree using the current document. Examines all the
        fold levels and tries to create a tree with them."""
        doc = self.coder.currentDoc
        if doc is None:
            return

        # check if we can parse this file
        if self.coder.currentDoc.GetLexer() not in [wx.stc.STC_LEX_PYTHON,
                                                    wx.stc.STC_LEX_CPP]:
            self.srcTree.DeleteAllItems()
            root = self.srcTree.AddRoot(
                'Source tree unavailable for this file type.')
            self.srcTree.SetItemImage(
                root, self._treeGfx['noDoc'],
                wx.TreeItemIcon_Normal)
            return

        # Go over file and get all the folds.
        # We do this instead of parsing the files ourselves since Scintilla
        # lexers are probably better than anything *I* can come up with. -mdc
        foldLines = []
        for lineno in range(doc.GetLineCount()):
            foldLevelFlags = doc.GetFoldLevel(lineno)
            foldLevel = \
                (foldLevelFlags & wx.stc.STC_FOLDLEVELNUMBERMASK) - \
                wx.stc.STC_FOLDLEVELBASE  # offset
            isFoldStart = (foldLevelFlags & wx.stc.STC_FOLDLEVELHEADERFLAG) > 0

            if isFoldStart:
                foldLines.append(
                    (foldLevel, lineno, doc.GetLineText(lineno).lstrip()))

        # Build the trees for the given language, this is a dictionary which
        # represents the hierarchy of the document. This system is dead simple,
        # determining what's a function/class based on what the Scintilla lexer
        # thinks should be folded. This is really fast and works most of the
        # time (prefectly for Python). In the future, we may need to specify
        # additional code to handle languages which don't have strict whitespace
        # requirements.
        #
        currentLexer = self.coder.currentDoc.GetLexer()
        if currentLexer == wx.stc.STC_LEX_CPP:
            stripChars = string.whitespace
            kwrds = CPP_DEFS
        elif currentLexer == wx.stc.STC_LEX_PYTHON:
            stripChars = string.whitespace + ':'
            kwrds = PYTHON_DEFS
        else:
            return  # do nothing here

        indent = doc.GetIndent()
        # filter out only definitions
        defineList = []
        lastItem = None
        for df in foldLines:
            lineText = doc.GetLineText(df[1]).lstrip()
            if not any([lineText.startswith(i) for i in kwrds]):
                continue

            if lastItem is not None:
                if df[0] > lastItem[3] + indent:
                    continue

            # slice off comment
            lineText = lineText.split('#')[0]
            lineTokens = [
                tok.strip(stripChars) for tok in re.split(
                    ' |\(|\)', lineText) if tok]

            # for some reason the line is valid but cannot be parsed, ignore it
            try:
                defType, defName = lineTokens[:2]
            except ValueError:
                continue

            lastItem = (defType, defName, df[1], df[0])
            defineList.append(lastItem)

        self.createSourceTree(defineList, doc.GetIndent())
        self.srcTree.Refresh()