def qt4():
    """PyOS_InputHook python hook for Qt4.

    Process pending Qt events and if there's no pending keyboard
    input, spend a short slice of time (50ms) running the Qt event
    loop.

    As a Python ctypes callback can't raise an exception, we catch
    the KeyboardInterrupt and temporarily deactivate the hook,
    which will let a *second* CTRL+C be processed normally and go
    back to a clean prompt line.
    """
    try:
        allow_CTRL_C()
        app = QtCore.QCoreApplication.instance()
        if not app:
            return 0
        app.processEvents(QtCore.QEventLoop.AllEvents, 300)
        if not stdin_ready():
            # Generally a program would run QCoreApplication::exec()
            # from main() to enter and process the Qt event loop until
            # quit() or exit() is called and the program terminates.
            #
            # For our input hook integration, we need to repeatedly
            # enter and process the Qt event loop for only a short
            # amount of time (say 50ms) to ensure that Python stays
            # responsive to other user inputs.
            #
            # A naive approach would be to repeatedly call
            # QCoreApplication::exec(), using a timer to quit after a
            # short amount of time. Unfortunately, QCoreApplication
            # emits an aboutToQuit signal before stopping, which has
            # the undesirable effect of closing all modal windows.
            #
            # To work around this problem, we instead create a
            # QEventLoop and call QEventLoop::exec(). Other than
            # setting some state variables which do not seem to be
            # used anywhere, the only thing QCoreApplication adds is
            # the aboutToQuit signal which is precisely what we are
            # trying to avoid.
            timer = QtCore.QTimer()
            event_loop = QtCore.QEventLoop()
            timer.timeout.connect(event_loop.quit)
            while not stdin_ready():
                timer.start(50)
                event_loop.exec_()
                timer.stop()
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt - Press Enter for new prompt")
    except: # NO exceptions are allowed to escape from a ctypes callback
        ignore_CTRL_C()
        from traceback import print_exc
        print_exc()
        print("Got exception from inputhook, unregistering.")
        clear_inputhook()
    finally:
        allow_CTRL_C()
    return 0