    def show_image(self, name):
        """Show image (item is a PIL image)"""
        command = "%s.show()" % name
        sw = self.shellwidget
        if sw._reading:
            sw.kernel_client.input(command)
        else:
            sw.execute(command)