    def setSysKB(self,button):
        if self.ostype == "XFCE":
            Popen(['xfce4-keyboard-settings'])
        else:
            Popen(['gnome-control-center','keyboard'])