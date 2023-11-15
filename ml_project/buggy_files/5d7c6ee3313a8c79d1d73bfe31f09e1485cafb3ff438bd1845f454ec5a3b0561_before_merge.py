        def pairing_step(code: str, device_response: Callable[[], bool]) -> bool:
            msg = "Please compare and confirm the pairing code on your BitBox02:\n" + code
            self.handler.show_message(msg)
            try:
                res = device_response()
            except:
                # Close the hid device on exception
                with self.device_manager().hid_lock:
                    hid_device.close()
                raise
            finally:
                self.handler.finished()
            return res