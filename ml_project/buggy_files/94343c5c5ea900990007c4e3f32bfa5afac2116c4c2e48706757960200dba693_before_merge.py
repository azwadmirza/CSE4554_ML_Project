    def imshow(self, name):
        """Show item's image"""
        self.shellwidget.execute("%%varexp --imshow %s" % name)