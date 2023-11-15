    def setConfig(self,button):
        try:
            if os.path.exists('/opt/sublime_text/sublime_text'):
                Popen(['/opt/sublime_text/sublime_text',os.environ['HOME']+'/.config/kinto/kinto.py'])
            elif which(gedit) is not None:
                Popen(['gedit',os.environ['HOME']+'/.config/kinto/kinto.py'])
            elif which(mousepad) is not None:
                Popen(['mousepad',os.environ['HOME']+'/.config/kinto/kinto.py'])

        except CalledProcessError:                                  # Notify user about error on running restart commands.
            Popen(['notify-send','Kinto: Error could not open config file!'])