    def scan(self, s, parent):
        '''Create an outline from a MindMap (.csv) file.'''
        # pylint: disable=no-member
        # pylint confuses this module with the stdlib json module
        c, d, self.gnx_dict = self.c, json.loads(s), {}
        for d2 in d.get('nodes', []):
            gnx = d2.get('gnx')
            self.gnx_dict[gnx] = d2
        top_d = d.get('top')
        if top_d:
            # Don't set parent.h or parent.gnx or parent.v.u.
            parent.b = top_d.get('b') or ''
            self.create_nodes(parent, top_d)
            c.redraw()
        return bool(top_d)