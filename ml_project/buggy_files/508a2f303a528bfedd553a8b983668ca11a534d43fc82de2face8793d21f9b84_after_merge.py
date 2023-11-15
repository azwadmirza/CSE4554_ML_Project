    def put_help(self, c, s, short_title=''):
        '''Put the help command.'''
        trace = False and not g.unitTesting
        s = g.adjustTripleString(s.rstrip(), c.tab_width)
        if s.startswith('<') and not s.startswith('<<'):
            pass # how to do selective replace??
        pc = g.app.pluginsController
        table = (
            'viewrendered3.py',
            'viewrendered2.py',
            'viewrendered.py',
        )
        for name in table:
            if pc.isLoaded(name):
                if trace: g.trace('already loaded', name)
                vr = pc.loadOnePlugin(name)
                break
        else:
            if trace: g.trace('auto-loading viewrendered.py')
            vr = pc.loadOnePlugin('viewrendered.py')
        if vr:
            kw = {
                'c': c,
                'flags': 'rst',
                'kind': 'rst',
                'label': '',
                'msg': s,
                'name': 'Apropos',
                'short_title': short_title,
                'title': ''}
            vr.show_scrolled_message(tag='Apropos', kw=kw)
            c.bodyWantsFocus()
            if g.unitTesting:
                vr.close_rendering_pane(event={'c': c})
        elif g.unitTesting:
            pass
        else:
            g.es(s)
        return vr # For unit tests