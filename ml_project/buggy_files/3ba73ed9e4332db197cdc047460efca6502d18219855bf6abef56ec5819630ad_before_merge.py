    def load_data(self, filename, ext):
        try:
            return self.call_kernel(
                interrupt=True,
                blocking=True,
                timeout=CALL_KERNEL_TIMEOUT).load_data(filename, ext)
        except TimeoutError:
            msg = _("Data is too big to be loaded")
            return msg
        except UnpicklingError:
            return None