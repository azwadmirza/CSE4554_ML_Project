    def save_namespace(self, filename):
        try:
            return self.call_kernel(
                interrupt=True,
                blocking=True,
                display_error=True,
                timeout=CALL_KERNEL_TIMEOUT).save_namespace(filename)
        except TimeoutError:
            msg = _("Data is too big to be saved")
            return msg
        except (UnpicklingError, RuntimeError):
            return None