    async def sendfile(self) -> None:
        assert self.transport is not None
        loop = self.loop
        data = b"".join(self._sendfile_buffer)
        if hasattr(loop, "sendfile"):
            # Python 3.7+
            self.transport.write(data)
            await loop.sendfile(self.transport, self._fobj, self._offset, self._count)
            await super().write_eof()
            return

        self._fobj.seek(self._offset)
        out_socket = self.transport.get_extra_info("socket").dup()
        out_socket.setblocking(False)
        out_fd = out_socket.fileno()

        try:
            await loop.sock_sendall(out_socket, data)
            if not self._do_sendfile(out_fd):
                fut = loop.create_future()
                fut.add_done_callback(partial(self._done_fut, out_fd))
                loop.add_writer(out_fd, self._sendfile_cb, fut, out_fd)
                await fut
        except asyncio.CancelledError:
            raise
        except Exception:
            server_logger.debug("Socket error")
            self.transport.close()
        finally:
            out_socket.close()

        await super().write_eof()