    def setRegion(self,button):
        if self.ostype == "XFCE":
            Popen(['gnome-language-selector'])
        elif self.ostype == "KDE":
            self.queryConfig('kcmshell4 kcm_translations >/dev/null 2>&1 || kcmshell5 kcm_translations >/dev/null 2>&1')
        else:
            Popen(['gnome-control-center','region'])