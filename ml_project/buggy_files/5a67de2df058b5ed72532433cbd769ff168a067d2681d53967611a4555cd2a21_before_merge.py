    def handle(self, listener, client, addr):
        req = None
        try:
            parser = http.RequestParser(self.cfg, client)
            try:
                listener_name = listener.getsockname()
                if not self.cfg.keepalive:
                    req = six.next(parser)
                    self.handle_request(listener_name, req, client, addr)
                else:
                    # keepalive loop
                    proxy_protocol_info = req.proxy_protocol_info
                    while True:
                        req = None
                        with self.timeout_ctx():
                            req = six.next(parser)
                        if not req:
                            break
                        req.proxy_protocol_info = proxy_protocol_info
                        self.handle_request(listener_name, req, client, addr)
            except http.errors.NoMoreData as e:
                self.log.debug("Ignored premature client disconnection. %s", e)
            except StopIteration as e:
                self.log.debug("Closing connection. %s", e)
            except ssl.SSLError:
                exc_info = sys.exc_info()
                # pass to next try-except level
                six.reraise(exc_info[0], exc_info[1], exc_info[2])
            except socket.error:
                exc_info = sys.exc_info()
                # pass to next try-except level
                six.reraise(exc_info[0], exc_info[1], exc_info[2])
            except Exception as e:
                self.handle_error(req, client, addr, e)
        except ssl.SSLError as e:
            if e.args[0] == ssl.SSL_ERROR_EOF:
                self.log.debug("ssl connection closed")
                client.close()
            else:
                self.log.debug("Error processing SSL request.")
                self.handle_error(req, client, addr, e)
        except socket.error as e:
            if e.args[0] not in (errno.EPIPE, errno.ECONNRESET):
                self.log.exception("Socket error processing request.")
            else:
                if e.args[0] == errno.ECONNRESET:
                    self.log.debug("Ignoring connection reset")
                else:
                    self.log.debug("Ignoring EPIPE")
        except Exception as e:
            self.handle_error(req, client, addr, e)
        finally:
            util.close(client)