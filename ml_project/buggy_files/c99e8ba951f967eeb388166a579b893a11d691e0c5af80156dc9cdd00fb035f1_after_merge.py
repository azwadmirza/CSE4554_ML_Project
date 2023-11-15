    def selfInsertCommand(self, event, action='insert'):
        """
        Insert a character in the body pane.

        This is the default binding for all keys in the body pane.
        It handles undo, bodykey events, tabs, back-spaces and bracket matching.
        """
        trace = 'keys' in g.app.debug
        c, p, u, w = self.c, self.c.p, self.c.undoer, self.editWidget(event)
        undoType = 'Typing'
        if not w:
            return  # pragma: no cover (defensive)
        #@+<< set local vars >>
        #@+node:ekr.20150514063305.269: *5* << set local vars >> (selfInsertCommand)
        stroke = event.stroke if event else None
        ch = event.char if event else ''
        if ch == 'Return':
            ch = '\n'  # This fixes the MacOS return bug.
        if ch == 'Tab':
            ch = '\t'
        name = c.widget_name(w)
        oldSel = w.getSelectionRange() if name.startswith('body') else (None, None)
        oldText = p.b if name.startswith('body') else ''
        oldYview = w.getYScrollPosition()
        brackets = self.openBracketsList + self.closeBracketsList
        inBrackets = ch and g.checkUnicode(ch) in brackets
        #@-<< set local vars >>
        if not ch:
            return
        if trace: g.trace('ch', repr(ch)) # and ch in '\n\r\t'
        assert g.isStrokeOrNone(stroke)
        if g.doHook("bodykey1", c=c, p=p, ch=ch, oldSel=oldSel, undoType=undoType):
            return
        if ch == '\t':
            self.updateTab(event, p, w, smartTab=True)
        elif ch == '\b':
            # This is correct: we only come here if there no bindngs for this key.
            self.backwardDeleteCharacter(event)
        elif ch in ('\r', '\n'):
            ch = '\n'
            self.insertNewlineHelper(w, oldSel, undoType)
        elif ch in '\'"' and c.config.getBool('smart-quotes'):
            self.doSmartQuote(action, ch, oldSel, w)
        elif inBrackets and self.autocompleteBrackets:
            self.updateAutomatchBracket(p, w, ch, oldSel)
        elif ch:
            # Null chars must not delete the selection.
            self.doPlainChar(action, ch, event, inBrackets, oldSel, stroke, w)
        #
        # Common processing.
        # Set the column for up and down keys.
        spot = w.getInsertPoint()
        c.editCommands.setMoveCol(w, spot)
        #
        # Update the text and handle undo.
        newText = w.getAllText()
        if newText != oldText:
            # Call u.doTyping to honor the user's undo granularity.
            newSel = w.getSelectionRange()
            newInsert = w.getInsertPoint()
            newSel = w.getSelectionRange()
            newText = w.getAllText()  # Converts to unicode.
            u.doTyping(p, 'Typing', oldText, newText,
                oldSel=oldSel, oldYview=oldYview, newInsert=newInsert, newSel=newSel)
        g.doHook("bodykey2", c=c, p=p, ch=ch, oldSel=oldSel, undoType=undoType)