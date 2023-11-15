    def readWithElementTree(self, path, s):

        contents = g.toUnicode(s) if g.isPython3 else s
        try:
            xroot = ElementTree.fromstring(contents)
        except Exception as e:
            if path:
                message = 'bad .leo file: %s' % g.shortFileName(path)
            else:
                message = 'The clipboard is not a vaild .leo file'
            print('')
            g.es_print(message, color='red')
            g.es_print(g.toUnicode(e))
            print('')
            # #970: Just report failure here.
            return None
        g_element = xroot.find('globals')
        v_elements = xroot.find('vnodes')
        t_elements = xroot.find('tnodes')
        self.scanGlobals(g_element)
        gnx2body, gnx2ua = self.scanTnodes(t_elements)
        hidden_v = self.scanVnodes(gnx2body, self.gnx2vnode, gnx2ua, v_elements)
        self.handleBits()
        return hidden_v