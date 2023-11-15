    def plot(self, name, funcname):
        """Plot item"""
        sw = self.shellwidget
        if sw._reading:
            sw.dbg_exec_magic('varexp', '--%s %s' % (funcname, name))
        else:
            sw.execute("%%varexp --%s %s" % (funcname, name))