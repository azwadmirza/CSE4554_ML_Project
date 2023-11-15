    def readWithElementTree(self, path, s):

        contents = g.toUnicode(s)
        contents = contents.translate(self.translate_table)
            # Fix #1036 and #1046.
        try:
            xroot = ElementTree.fromstring(contents)
        except Exception as e:
            # #970: Just report failure here.
            if path:
                message = f"bad .leo file: {g.shortFileName(path)}"
            else:
                message = 'The clipboard is not a vaild .leo file'
            g.es_print('\n' + message, color='red')
            g.es_print(g.toUnicode(e))
            print('')
            # #1510: Return a tuple.
            return None, None
        g_element = xroot.find('globals')
        v_elements = xroot.find('vnodes')
        t_elements = xroot.find('tnodes')
        gnx2body, gnx2ua = self.scanTnodes(t_elements)
        hidden_v = self.scanVnodes(gnx2body, self.gnx2vnode, gnx2ua, v_elements)
        self.handleBits()
        return hidden_v, g_element