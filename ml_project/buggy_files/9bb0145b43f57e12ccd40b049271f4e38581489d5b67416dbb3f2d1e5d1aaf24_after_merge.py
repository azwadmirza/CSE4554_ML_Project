    def setSysKB(self,button):
        if self.ostype == "XFCE":
            Popen(['xfce4-keyboard-settings'])
        elif self.ostype == "KDE":
            self.queryConfig('systemsettings >/dev/null 2>&1 || systemsettings5 >/dev/null 2>&1')
        else:
            Popen(['gnome-control-center','keyboard'])