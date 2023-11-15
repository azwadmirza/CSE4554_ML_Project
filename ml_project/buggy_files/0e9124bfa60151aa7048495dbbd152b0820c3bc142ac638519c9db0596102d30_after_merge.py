def alwaysIndentBody(self, event=None):
    """
    The always-indent-region command indents each line of the selected body
    text. The @tabwidth directive in effect determines amount of
    indentation.
    """
    c, p, u, w = self, self.p, self.undoer, self.frame.body.wrapper
    #
    # #1801: Don't rely on bindings to ensure that we are editing the body.
    event_w = event and event.w
    if event_w != w:
        c.insertCharFromEvent(event)
        return
    #
    # "Before" snapshot.
    bunch = u.beforeChangeBody(p)
    #
    # Initial data.
    sel_1, sel_2 = w.getSelectionRange()
    tab_width = c.getTabWidth(p)
    head, lines, tail, oldSel, oldYview = self.getBodyLines()
    #
    # Calculate the result.
    changed, result = False, []
    for line in lines:
        i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        s = g.computeLeadingWhitespace(width + abs(tab_width), tab_width) + line[i:]
        if s != line:
            changed = True
        result.append(s)
    if not changed:
        return
    #
    # Set p.b and w's text first.
    middle = ''.join(result)
    all = head + middle + tail
    p.b = all # Sets dirty and changed bits.
    w.setAllText(all)
    #
    # Calculate the proper selection range (i, j, ins).
    if sel_1 == sel_2:
        line = result[0]
        i, width = g.skip_leading_ws_with_indent(line, 0, tab_width)
        i = j = len(head) + i
    else:
        i = len(head)
        j = len(head) + len(middle)
        if middle.endswith('\n'):  # #1742.
            j -= 1
    #
    # Set the selection range and scroll position.
    w.setSelectionRange(i, j, insert=j)
    w.setYScrollPosition(oldYview)
    #
    # "after" snapshot.
    u.afterChangeBody(p, 'Indent Region', bunch)