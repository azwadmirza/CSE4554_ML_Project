    def blacken_tree(self, root, diff_flag, check_flag=False):
        """Run black on all Python @<file> nodes in root's tree."""
        c = self.c
        if not black or not root:
            return
        t1 = time.process_time()
        self.changed, self.errors, self.total = 0, 0, 0
        undo_type = 'blacken-tree'
        bunch = c.undoer.beforeChangeTree(root)
        # Blacken *only* the selected tree.
        changed = False
        for p in root.self_and_subtree():
            if self.blacken_node_helper(p, check_flag, diff_flag):
                changed = True
        if changed:
            c.setChanged(True)
            c.undoer.afterChangeTree(root, undo_type, bunch)
        t2 = time.process_time()
        if not g.unitTesting:
            print(
                f'{root.h}: scanned {self.total} node{g.plural(self.total)}, '
                f'changed {self.changed} node{g.plural(self.changed)}, '
                f'{self.errors} error{g.plural(self.errors)} '
                f'in {t2-t1:5.2f} sec.'
            )
        if self.changed and not c.changed:
            c.setChanged(True)
        if self.changed or self.errors:
            c.redraw()