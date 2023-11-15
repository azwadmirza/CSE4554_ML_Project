    def updateSaxClone(self, sax_node, parent_v, v):
        '''
        Update the body text of v. It overrides any previous body text.
        '''
        at = self.c.atFileCommands
        b = sax_node.bodyString
        if v.b != b:
            v.setBodyString(b)
            at.bodySetInited(v)