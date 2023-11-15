    def scan(self, s, parent):
        '''Create an outline from a MindMap (.csv) file.'''
        # pylint: disable=no-member
        # pylint confuses this module with the stdlib json module
        c, d, self.gnx_dict = self.c, json.loads(s), {}
        try:
            for d2 in d.get('nodes', []):
                gnx = d2.get('gnx')
                self.gnx_dict[gnx] = d2
            top_d = d.get('top')
            if top_d:
                # Don't set parent.h or parent.gnx or parent.v.u.
                parent.b = top_d.get('b') or ''
                self.create_nodes(parent, top_d)
                c.redraw()
        except AttributeError:
            # Partial fix for #1098: issue advice.
            g.error('Can not import %s' % parent.h)
            g.es('Leo can only read .json files that Leo itself wrote')
            g.es('Workaround: copy your .json text into @auto x.json.')
            g.es('Leo will read the file correctly when you reload your outline.')
        return bool(top_d)