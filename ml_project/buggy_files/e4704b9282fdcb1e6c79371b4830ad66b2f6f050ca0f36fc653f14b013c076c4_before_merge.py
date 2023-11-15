def indentBody(self, event=None):
    """
    The indent-region command indents each line of the selected body text.
    Unlike the always-indent-region command, this command inserts a tab
    (soft or hard) when there is no selected text.
    
    The @tabwidth directive in effect determines amount of indentation.
    """
    c, w = self, self.frame.body.wrapper
    # # 1739. Special case for a *plain* tab bound to indent-region.
    sel_1, sel_2 = w.getSelectionRange()
    if sel_1 == sel_2:
        char = getattr(event, 'char', None)
        stroke = getattr(event, 'stroke', None)
        if char == '\t' and stroke and stroke.isPlainKey():
            c.editCommands.selfInsertCommand(event)  # Handles undo.
            return
    c.alwaysIndentBody(event)