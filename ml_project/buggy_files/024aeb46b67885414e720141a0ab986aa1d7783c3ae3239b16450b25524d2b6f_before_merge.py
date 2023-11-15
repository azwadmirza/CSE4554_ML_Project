    def show_image(self, name):
        """Show image (item is a PIL image)"""
        command = "%s.show()" % name
        self.shellwidget.execute(command)