    def _cancel_current_command(self, waiter):
        async def cancel():
            try:
                # Open new connection to the server
                r, w = await connect_utils._open_connection(
                    loop=self._loop, addr=self._addr, params=self._params)
            except Exception as ex:
                waiter.set_exception(ex)
                return

            try:
                # Pack CancelRequest message
                msg = struct.pack('!llll', 16, 80877102,
                                  self._protocol.backend_pid,
                                  self._protocol.backend_secret)

                w.write(msg)
                await r.read()  # Wait until EOF
            except ConnectionResetError:
                # On some systems Postgres will reset the connection
                # after processing the cancellation command.
                pass
            except Exception as ex:
                waiter.set_exception(ex)
            finally:
                if not waiter.done():  # Ensure set_exception wasn't called.
                    waiter.set_result(None)
                w.close()

        self._loop.create_task(cancel())