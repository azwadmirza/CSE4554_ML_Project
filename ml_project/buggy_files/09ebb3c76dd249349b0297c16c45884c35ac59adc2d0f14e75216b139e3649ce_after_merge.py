    def _wait(self, condition, signal, timeout_msg, timeout):
        """
        Wait until condition() is True by running an event loop.

        signal: qt signal that should interrupt the event loop.
        timeout_msg: Message to display in case of a timeout.
        timeout: time in seconds before a timeout
        """
        # Exit if condition is fulfilled or the kernel is dead.
        if condition():
            return
        if not self.kernel_client.is_alive():
            raise RuntimeError("Kernel is dead")

        # Create event loop to wait with
        wait_loop = QEventLoop()
        wait_timeout = QTimer()
        wait_timeout.setSingleShot(True)

        # Connect signals to stop kernel loop
        wait_timeout.timeout.connect(wait_loop.quit)
        self.kernel_client.hb_channel.kernel_died.connect(wait_loop.quit)
        signal.connect(wait_loop.quit)

        # Wait until the kernel returns the value
        wait_timeout.start(timeout * 1000)
        while not condition():
            if not wait_timeout.isActive():
                signal.disconnect(wait_loop.quit)
                self.kernel_client.hb_channel.kernel_died.disconnect(
                    wait_loop.quit)
                if condition():
                    return
                if not self.kernel_client.is_alive():
                    raise RuntimeError("Kernel is dead")
                raise TimeoutError(timeout_msg)
            wait_loop.exec_()

        wait_timeout.stop()
        signal.disconnect(wait_loop.quit)
        self.kernel_client.hb_channel.kernel_died.disconnect(
            wait_loop.quit)