    def plot(self, name, funcname):
        """Plot item"""
        self.shellwidget.execute("%%varexp --%s %s" % (funcname, name))