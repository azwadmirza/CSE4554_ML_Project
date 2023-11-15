def refreshFromDisk(self, event=None):
    """Refresh an @<file> node from disk."""
    c, p, u = self, self.p, self.undoer
    c.nodeConflictList = []
    fn = p.anyAtFileNodeName()
    shouldDelete = c.sqlite_connection is None
    if not fn:
        g.warning(f"not an @<file> node: {p.h!r}")
        return
    # #1603.
    if os.path.isdir(fn):
        g.warning(f"not a file: {fn!r}")
        return
    b = u.beforeChangeTree(p)
    redraw_flag = True
    at = c.atFileCommands
    c.recreateGnxDict()
        # Fix bug 1090950 refresh from disk: cut node ressurection.
    i = g.skip_id(p.h, 0, chars='@')
    word = p.h[0:i]
    if word == '@auto':
        # This includes @auto-*
        if shouldDelete: p.v._deleteAllChildren()
        # Fix #451: refresh-from-disk selects wrong node.
        p = at.readOneAtAutoNode(fn, p)
    elif word in ('@thin', '@file'):
        if shouldDelete: p.v._deleteAllChildren()
        at.read(p, force=True)
    elif word == '@clean':
        # Wishlist 148: use @auto parser if the node is empty.
        if p.b.strip() or p.hasChildren():
            at.readOneAtCleanNode(p)
        else:
            # Fix #451: refresh-from-disk selects wrong node.
            p = at.readOneAtAutoNode(fn, p)
    elif word == '@shadow':
        if shouldDelete: p.v._deleteAllChildren()
        at.read(p, force=True, atShadow=True)
    elif word == '@edit':
        at.readOneAtEditNode(fn, p)
            # Always deletes children.
    elif word == '@asis':
        # Fix #1067.
        at.readOneAtAsisNode(fn, p)
            # Always deletes children.
    else:
        g.es_print(f"can not refresh from disk\n{p.h!r}")
        redraw_flag = False
    if redraw_flag:
        # Fix #451: refresh-from-disk selects wrong node.
        c.selectPosition(p)
        u.afterChangeTree(p, command='refresh-from-disk', bunch=b)
        # Create the 'Recovered Nodes' tree.
        c.fileCommands.handleNodeConflicts()
        c.redraw()