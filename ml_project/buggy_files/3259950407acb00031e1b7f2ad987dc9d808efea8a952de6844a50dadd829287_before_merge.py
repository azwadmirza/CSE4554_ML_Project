    def setRegion(self,button):
        if self.ostype == "XFCE":
            Popen(['gnome-language-selector'])
        else:
            Popen(['gnome-control-center','region'])