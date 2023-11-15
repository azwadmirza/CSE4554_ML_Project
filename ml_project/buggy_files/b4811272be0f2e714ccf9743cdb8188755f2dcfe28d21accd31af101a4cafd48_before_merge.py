    def _wait(self, condition, signal, timeout_msg, timeout):
        """
        Wait until condition() is True by running an event loop.

        signal: qt signal that should interrupt the event loop.
        timeout_msg: Meaage to display in case of a timeout.
        timeout: time in seconds before a timeout
        """
        if condition():
            return

        # Create event loop to wait with
        wait_loop = QEventLoop()
        signal.connect(wait_loop.quit)
        wait_timeout = QTimer()
        wait_timeout.setSingleShot(True)
        wait_timeout.timeout.connect(wait_loop.quit)

        # Wait until the kernel returns the value
        wait_timeout.start(timeout * 1000)
        while not condition():
            if not wait_timeout.isActive():
                signal.disconnect(wait_loop.quit)
                if not condition():
                    raise TimeoutError(timeout_msg)
                return
            wait_loop.exec_()

        wait_timeout.stop()
        signal.disconnect(wait_loop.quit)