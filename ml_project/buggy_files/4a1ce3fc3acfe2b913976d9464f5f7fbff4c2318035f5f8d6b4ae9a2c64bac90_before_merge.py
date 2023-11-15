    def doTyping(self, p, undo_type, oldText, newText,
        newInsert=None, oldSel=None, newSel=None, oldYview=None,
    ):
        """
        Save enough information to undo or redo a typing operation efficiently,
        that is, with the proper granularity.
        
        Do nothing when called from the undo/redo logic because the Undo
        and Redo commands merely reset the bead pointer.
        
        **Important**: Code should call this method *only* when the user has
        actually typed something. Commands should use u.beforeChangeBody and
        u.afterChangeBody.
        
        Only qtm.onTextChanged and ec.selfInsertCommand now call this method.
        """
        c, u, w = self.c, self, self.c.frame.body.wrapper
        # Leo 6.4: undo_type must be 'Typing'.
        undo_type = undo_type.capitalize()
        assert undo_type == 'Typing', (repr(undo_type), g.callers())
        #@+<< return if there is nothing to do >>
        #@+node:ekr.20040324061854: *5* << return if there is nothing to do >>
        if u.redoing or u.undoing:
            return None
        if undo_type is None:
            return None
        if undo_type == "Can't Undo":
            u.clearUndoState()
            u.setUndoTypes()  # Must still recalculate the menu labels.
            return None
        if oldText == newText:
            u.setUndoTypes()  # Must still recalculate the menu labels.
            return None
        #@-<< return if there is nothing to do >>
        #@+<< init the undo params >>
        #@+node:ekr.20040324061854.1: *5* << init the undo params >>
        u.clearOptionalIvars()
        # Set the params.
        u.undoType = undo_type
        u.p = p.copy()
        #@-<< init the undo params >>
        #@+<< compute leading, middle & trailing  lines >>
        #@+node:ekr.20031218072017.1491: *5* << compute leading, middle & trailing  lines >>
        #@+at Incremental undo typing is similar to incremental syntax coloring. We compute
        # the number of leading and trailing lines that match, and save both the old and
        # new middle lines. NB: the number of old and new middle lines may be different.
        #@@c
        old_lines = oldText.split('\n')
        new_lines = newText.split('\n')
        new_len = len(new_lines)
        old_len = len(old_lines)
        min_len = min(old_len, new_len)
        i = 0
        while i < min_len:
            if old_lines[i] != new_lines[i]:
                break
            i += 1
        leading = i
        if leading == new_len:
            # This happens when we remove lines from the end.
            # The new text is simply the leading lines from the old text.
            trailing = 0
        else:
            i = 0
            while i < min_len - leading:
                if old_lines[old_len - i - 1] != new_lines[new_len - i - 1]:
                    break
                i += 1
            trailing = i
        # NB: the number of old and new middle lines may be different.
        if trailing == 0:
            old_middle_lines = old_lines[leading:]
            new_middle_lines = new_lines[leading:]
        else:
            old_middle_lines = old_lines[leading : -trailing]
            new_middle_lines = new_lines[leading : -trailing]
        # Remember how many trailing newlines in the old and new text.
        i = len(oldText) - 1; old_newlines = 0
        while i >= 0 and oldText[i] == '\n':
            old_newlines += 1
            i -= 1
        i = len(newText) - 1; new_newlines = 0
        while i >= 0 and newText[i] == '\n':
            new_newlines += 1
            i -= 1
        #@-<< compute leading, middle & trailing  lines >>
        #@+<< save undo text info >>
        #@+node:ekr.20031218072017.1492: *5* << save undo text info >>
        u.oldText = None
        u.newText = None
        u.leading = leading
        u.trailing = trailing
        u.oldMiddleLines = old_middle_lines
        u.newMiddleLines = new_middle_lines
        u.oldNewlines = old_newlines
        u.newNewlines = new_newlines
        #@-<< save undo text info >>
        #@+<< save the selection and scrolling position >>
        #@+node:ekr.20040324061854.2: *5* << save the selection and scrolling position >>
        # Remember the selection.
        u.oldSel = oldSel
        u.newSel = newSel
        # Remember the scrolling position.
        if oldYview:
            u.yview = oldYview
        else:
            u.yview = c.frame.body.wrapper.getYScrollPosition()
        #@-<< save the selection and scrolling position >>
        #@+<< adjust the undo stack, clearing all forward entries >>
        #@+node:ekr.20040324061854.3: *5* << adjust the undo stack, clearing all forward entries >>
        #@+at
        # New in Leo 4.3. Instead of creating a new bead on every character, we
        # may adjust the top bead:
        # word granularity: adjust the top bead if the typing would continue the word.
        # line granularity: adjust the top bead if the typing is on the same line.
        # node granularity: adjust the top bead if the typing is anywhere on the same node.
        #@@c
        granularity = u.granularity
        old_d = u.peekBead(u.bead)
        old_p = old_d and old_d.get('p')
        #@+<< set newBead if we can't share the previous bead >>
        #@+node:ekr.20050125220613: *6* << set newBead if we can't share the previous bead >>
        # Set newBead to True if undo_type is not 'Typing' so that commands that
        # get treated like typing (by onBodyChanged) don't get lumped
        # with 'real' typing.
        #@@c
        if (
            not old_d or not old_p or
            old_p.v != p.v or
            old_d.get('kind') != 'typing' or
            old_d.get('undoType') != 'Typing' or
            undo_type != 'Typing'
        ):
            newBead = True  # We can't share the previous node.
        elif granularity == 'char':
            newBead = True  # This was the old way.
        elif granularity == 'node':
            newBead = False  # Always replace previous bead.
        else:
            assert granularity in ('line', 'word')
            # Replace the previous bead if only the middle lines have changed.
            newBead = (
                old_d.get('leading', 0) != u.leading or
                old_d.get('trailing', 0) != u.trailing
            )
            if granularity == 'word' and not newBead:
                # Protect the method that may be changed by the user
                try:
                    #@+<< set newBead if the change does not continue a word >>
                    #@+node:ekr.20050125203937: *7* << set newBead if the change does not continue a word >>
                    # Fix #653: undoer problem: be wary of the ternary operator here.
                    old_start = old_end = new_start = new_end = 0
                    if oldSel:
                        old_start, old_end = oldSel
                    if newSel:
                        new_start, new_end = newSel
                    prev_start, prev_end = u.prevSel
                    if old_start != old_end or new_start != new_end:
                        # The new and old characters are not contiguous.
                        newBead = True
                    else:
                        # 2011/04/01: Patch by Sam Hartsfield
                        old_row, old_col = g.convertPythonIndexToRowCol(
                            oldText, old_start)
                        new_row, new_col = g.convertPythonIndexToRowCol(
                            newText, new_start)
                        prev_row, prev_col = g.convertPythonIndexToRowCol(
                            oldText, prev_start)
                        old_lines = g.splitLines(oldText)
                        new_lines = g.splitLines(newText)
                        # Recognize backspace, del, etc. as contiguous.
                        if old_row != new_row or abs(old_col - new_col) != 1:
                            # The new and old characters are not contiguous.
                            newBead = True
                        elif old_col == 0 or new_col == 0:
                            # py-lint: disable=W0511
                            # W0511:1362: TODO
                            # TODO this is not true, we might as well just have entered a
                            # char at the beginning of an existing line
                            pass  # We have just inserted a line.
                        else:
                            # 2011/04/01: Patch by Sam Hartsfield
                            old_s = old_lines[old_row]
                            new_s = new_lines[new_row]
                            # New in 4.3b2:
                            # Guard against invalid oldSel or newSel params.
                            if old_col - 1 >= len(old_s) or new_col - 1 >= len(new_s):
                                newBead = True
                            else:
                                old_ch = old_s[old_col - 1]
                                new_ch = new_s[new_col - 1]
                                newBead = self.recognizeStartOfTypingWord(
                                    old_lines, old_row, old_col, old_ch,
                                    new_lines, new_row, new_col, new_ch,
                                    prev_row, prev_col)
                    #@-<< set newBead if the change does not continue a word >>
                except Exception:
                    g.error('Unexpected exception...')
                    g.es_exception()
                    newBead = True
        #@-<< set newBead if we can't share the previous bead >>
        # Save end selection as new "previous" selection
        u.prevSel = u.newSel
        if newBead:
            # Push params on undo stack, clearing all forward entries.
            bunch = g.Bunch(
                p=p.copy(),
                kind='typing',  # lowercase.
                undoType=undo_type,  # capitalized.
                undoHelper=u.undoTyping,
                redoHelper=u.redoTyping,
                oldMarked=old_p.isMarked() if old_p else p.isMarked(), # #1694
                oldText=u.oldText,
                oldSel=u.oldSel,
                oldNewlines=u.oldNewlines,
                oldMiddleLines=u.oldMiddleLines,
            )
            u.pushBead(bunch)
        else:
            bunch = old_d
        bunch.leading = u.leading
        bunch.trailing = u.trailing
        bunch.newMarked = p.isMarked()  # #1694 
        bunch.newNewlines = u.newNewlines
        bunch.newMiddleLines = u.newMiddleLines
        bunch.newSel = u.newSel
        bunch.newText = u.newText
        bunch.yview = u.yview
        #@-<< adjust the undo stack, clearing all forward entries >>
        if 'undo' in g.app.debug and 'verbose' in g.app.debug:
            print(f"u.doTyping: {len(oldText)} => {len(newText)}")
        if u.per_node_undo:
            u.putIvarsToVnode(p)
        #
        # Finish updating the text.
        p.v.setBodyString(newText)
        u.updateAfterTyping(p, w)