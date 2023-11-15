    def make_at_clean_outline(self, fn, root, s, rev):
        '''
        Create a hidden temp outline from lines without sentinels.
        root is the @<file> node for fn.
        s is the contents of the (public) file, without sentinels.
        '''
        # A specialized version of at.readOneAtCleanNode.
        hidden_c = leoCommands.Commands(fn, gui=g.app.nullGui)
        at = hidden_c.atFileCommands
        x = hidden_c.shadowController
        hidden_c.frame.createFirstTreeNode()
        hidden_root = hidden_c.rootPosition()
        # copy root to hidden root, including gnxs.
        root.copyTreeFromSelfTo(hidden_root, copyGnxs=True)
        hidden_root.h = fn + ':' + rev if rev else fn
        # Set at.encoding first.
        at.initReadIvars(hidden_root, fn)
            # Must be called before at.scanAllDirectives.
        at.scanAllDirectives(hidden_root)
            # Sets at.startSentinelComment/endSentinelComment.
        new_public_lines = g.splitLines(s)
        old_private_lines = at.write_at_clean_sentinels(hidden_root)
        marker = x.markerFromFileLines(old_private_lines, fn)
        old_public_lines, junk = x.separate_sentinels(old_private_lines, marker)
        assert old_public_lines
        new_private_lines = x.propagate_changed_lines(
            new_public_lines, old_private_lines, marker, p=hidden_root)
        at.fast_read_into_root(
            c = hidden_c,
            contents = ''.join(new_private_lines),
            gnx2vnode = {},
            path = fn,
            root = hidden_root,
        )
        return hidden_c