    def qt_nt_inputhook():
        """Qt input hook for Windows
        
        This input hook wait for available stdin data (notified by
        ExternalPythonShell through the monitor's inputhook_flag
        attribute), and in the meantime it processes Qt events.
        """
        # Qt imports
        if os.environ["QT_API"] == 'pyqt5':
            from PyQt5 import QtCore
        elif os.environ["QT_API"] == 'pyqt':
            from PyQt4 import QtCore           # analysis:ignore
        elif os.environ["QT_API"] == 'pyside':
            from PySide import QtCore          # analysis:ignore

        # Refreshing variable explorer, except on first input hook call:
        # (otherwise, on slow machines, this may freeze Spyder)
        monitor.refresh_from_inputhook()
        if os.name == 'nt':
            try:
                # This call fails for Python without readline support
                # (or on Windows platforms) when PyOS_InputHook is called
                # for the second consecutive time, because the 100-bytes
                # stdin buffer is full.
                # For more details, see the `PyOS_StdioReadline` function
                # in Python source code (Parser/myreadline.c)
                sys.stdin.tell()
            except IOError:
                return 0
        app = QtCore.QCoreApplication.instance()
        if app and app.thread() is QtCore.QThread.currentThread():
            timer = QtCore.QTimer()
            timer.timeout.connect(app.quit)
            monitor.toggle_inputhook_flag(False)
            while not monitor.inputhook_flag:
                timer.start(50)
                QtCore.QCoreApplication.exec_()
                timer.stop()
#            # Socket-based alternative:
#            socket = QtNetwork.QLocalSocket()
#            socket.connectToServer(os.environ['SPYDER_SHELL_ID'])
#            socket.waitForConnected(-1)
#            while not socket.waitForReadyRead(10):
#                timer.start(50)
#                QtCore.QCoreApplication.exec_()
#                timer.stop()
#            socket.read(3)
#            socket.disconnectFromServer()
        return 0