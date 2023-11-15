    def setService(self,button):
        try:
            if os.path.exists('/opt/sublime_text/sublime_text'):
                Popen(['/opt/sublime_text/sublime_text','/lib/systemd/system/xkeysnail.service'])
            elif which('gedit') is not None:
                Popen(['gedit','/lib/systemd/system/xkeysnail.service'])
            elif which('mousepad') is not None:
                Popen(['mousepad','/lib/systemd/system/xkeysnail.service'])
            elif which('kate') is not None:
                Popen(['kate','/lib/systemd/system/xkeysnail.service'])
            elif which('kwrite') is not None:
                Popen(['kwrite','/lib/systemd/system/xkeysnail.service'])

        except CalledProcessError:                                  # Notify user about error on running restart commands.
            Popen(['notify-send','Kinto: Error could not open config file!'])