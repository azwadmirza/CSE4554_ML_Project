    def _create_launchers(self):
        """Create launchers"""

        self._print("Creating launchers")
        self.create_launcher('WinPython Command Prompt.exe', 'cmd.ico',
                             command='$SYSDIR\cmd.exe',
                             args=r'/k cmd.bat')        
        
        self.create_launcher('WinPython Interpreter.exe', 'python.ico',
                             command='$SYSDIR\cmd.exe',
                             args= r'/k winpython.bat')

        #self.create_launcher('IDLEX (students).exe', 'python.ico',
        #                     command='$SYSDIR\cmd.exe',
        #                     args= r'/k IDLEX_for_student.bat  %*',
        #                     workdir='$EXEDIR\scripts')
        self.create_launcher('IDLEX (Python GUI).exe', 'python.ico',
                             command='wscript.exe',
                             args= r'Noshell.vbs IDLEX.bat')

        self.create_launcher('Spyder.exe', 'spyder.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs spyder.bat')

        self.create_launcher('Spyder reset.exe', 'spyder_reset.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs spyder_reset.bat')

        self.create_launcher('WinPython Control Panel.exe', 'winpython.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs wpcp.bat')

        # Multi-Qt launchers (Qt5 has priority if found)
        self.create_launcher('Qt Demo.exe', 'qt.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs qtdemo.bat')

        self.create_launcher('Qt Assistant.exe', 'qtassistant.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs qtassistant.bat')

        self.create_launcher('Qt Designer.exe', 'qtdesigner.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs qtdesigner.bat')

        self.create_launcher('Qt Linguist.exe', 'qtlinguist.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs qtlinguist.bat')

        # Jupyter launchers
        self.create_launcher('IPython Qt Console.exe', 'ipython.ico',
                             command='wscript.exe',
                             args=r'Noshell.vbs qtconsole.bat')

        # this one needs a shell to kill fantom processes
        self.create_launcher('Jupyter Notebook.exe', 'jupyter.ico',
                             command='$SYSDIR\cmd.exe',
                             args=r'/k ipython_notebook.bat')

        self._print_done()