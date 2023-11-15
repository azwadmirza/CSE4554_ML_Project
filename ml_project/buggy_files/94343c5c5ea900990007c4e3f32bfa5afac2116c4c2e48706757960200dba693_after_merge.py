    def imshow(self, name):
        """Show item's image"""
        sw = self.shellwidget
        if sw._reading:
            sw.dbg_exec_magic('varexp', '--imshow %s' % name)
        else:
            sw.execute("%%varexp --imshow %s" % name)