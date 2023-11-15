    def enable(self, app=None):
        """Enable event loop integration with PyQt4.
        
        Parameters
        ----------
        app : Qt Application, optional.
            Running application to use.  If not given, we probe Qt for an
            existing application object, and create a new one if none is found.

        Notes
        -----
        This methods sets the PyOS_InputHook for PyQt4, which allows
        the PyQt4 to integrate with terminal based applications like
        IPython.

        If ``app`` is not given we probe for an existing one, and return it if
        found.  If no existing app is found, we create an :class:`QApplication`
        as follows::

            from PyQt4 import QtCore
            app = QtGui.QApplication(sys.argv)
        """
        from IPython.lib.inputhookqt4 import create_inputhook_qt4
        from IPython.external.appnope import nope
        app, inputhook_qt4 = create_inputhook_qt4(self, app)
        self.manager.set_inputhook(inputhook_qt4)
        nope()

        return app