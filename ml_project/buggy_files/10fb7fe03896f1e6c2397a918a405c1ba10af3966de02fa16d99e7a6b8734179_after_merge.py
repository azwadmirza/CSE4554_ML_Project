def create_app(config):
    mode = config.MODE

    if mode & App.GuiMode:

        from PyQt5.QtGui import QIcon, QPixmap
        from PyQt5.QtWidgets import QApplication, QWidget

        from feeluown.compat import QEventLoop

        q_app = QApplication(sys.argv)
        q_app.setQuitOnLastWindowClosed(True)
        q_app.setApplicationName('FeelUOwn')

        app_event_loop = QEventLoop(q_app)
        asyncio.set_event_loop(app_event_loop)

        class GuiApp(QWidget):
            mode = App.GuiMode

            def __init__(self):
                super().__init__()
                self.setObjectName('app')
                QApplication.setWindowIcon(QIcon(QPixmap(APP_ICON)))

            def closeEvent(self, e):
                self.ui.mpv_widget.close()
                event_loop = asyncio.get_event_loop()
                event_loop.stop()

        class FApp(App, GuiApp):
            def __init__(self, config):
                App.__init__(self, config)
                GuiApp.__init__(self)

    else:
        FApp = App

    Signal.setup_aio_support()
    Resolver.setup_aio_support()
    app = FApp(config)
    attach_attrs(app)
    Resolver.library = app.library
    return app