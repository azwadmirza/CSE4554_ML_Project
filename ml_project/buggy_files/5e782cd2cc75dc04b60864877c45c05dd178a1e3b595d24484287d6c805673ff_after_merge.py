    def blacken_node(self, root, diff_flag, check_flag=False):
        """Run black on all Python @<file> nodes in root's tree."""
        c = self.c
        if not black or not root:
            return
        t1 = time.process_time()
        self.changed, self.errors, self.total = 0, 0, 0
        self.undo_type = 'blacken-node'
        self.blacken_node_helper(root, check_flag, diff_flag)
        t2 = time.process_time()
        if not g.unitTesting:
            print(
                f'{root.h}: scanned {self.total} node{g.plural(self.total)}, '
                f'changed {self.changed} node{g.plural(self.changed)}, '
                f'{self.errors} error{g.plural(self.errors)} '
                f'in {t2-t1:5.2f} sec.'
            )
        if self.changed or self.errors:
            c.redraw()