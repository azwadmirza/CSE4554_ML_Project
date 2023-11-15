    async def start(self) -> None:
        """Process incoming request.

        It reads request line, request headers and request payload, then
        calls handle_request() method. Subclass has to override
        handle_request(). start() handles various exceptions in request
        or response handling. Connection is being closed always unless
        keep_alive(True) specified.
        """
        loop = self._loop
        handler = self._task_handler
        assert handler is not None
        manager = self._manager
        assert manager is not None
        keepalive_timeout = self._keepalive_timeout
        resp = None
        assert self._request_factory is not None
        assert self._request_handler is not None

        while not self._force_close:
            if not self._messages:
                try:
                    # wait for next request
                    self._waiter = loop.create_future()
                    await self._waiter
                except asyncio.CancelledError:
                    break
                finally:
                    self._waiter = None

            message, payload = self._messages.popleft()

            if self.access_log:
                now = loop.time()

            manager.requests_count += 1
            writer = StreamWriter(self, loop)
            request = self._request_factory(
                message, payload, self, writer, handler)
            try:
                try:
                    # a new task is used for copy context vars (#3406)
                    task = self._loop.create_task(
                        self._request_handler(request))
                    resp = await task
                except HTTPException as exc:
                    resp = exc
                except asyncio.CancelledError:
                    self.log_debug('Ignored premature client disconnection')
                    break
                except asyncio.TimeoutError as exc:
                    self.log_debug('Request handler timed out.', exc_info=exc)
                    resp = self.handle_error(request, 504)
                except Exception as exc:
                    resp = self.handle_error(request, 500, exc)
                else:
                    # Deprecation warning (See #2415)
                    if getattr(resp, '__http_exception__', False):
                        warnings.warn(
                            "returning HTTPException object is deprecated "
                            "(#2415) and will be removed, "
                            "please raise the exception instead",
                            DeprecationWarning)

                if self.debug:
                    if not isinstance(resp, StreamResponse):
                        if resp is None:
                            raise RuntimeError("Missing return "
                                               "statement on request handler")
                        else:
                            raise RuntimeError("Web-handler should return "
                                               "a response instance, "
                                               "got {!r}".format(resp))
                await resp.prepare(request)
                await resp.write_eof()

                # notify server about keep-alive
                self._keepalive = bool(resp.keep_alive)

                # log access
                if self.access_log:
                    self.log_access(request, resp, loop.time() - now)

                # check payload
                if not payload.is_eof():
                    lingering_time = self._lingering_time
                    if not self._force_close and lingering_time:
                        self.log_debug(
                            'Start lingering close timer for %s sec.',
                            lingering_time)

                        now = loop.time()
                        end_t = now + lingering_time

                        with suppress(
                                asyncio.TimeoutError, asyncio.CancelledError):
                            while not payload.is_eof() and now < end_t:
                                with CeilTimeout(end_t - now, loop=loop):
                                    # read and ignore
                                    await payload.readany()
                                now = loop.time()

                    # if payload still uncompleted
                    if not payload.is_eof() and not self._force_close:
                        self.log_debug('Uncompleted request.')
                        self.close()

                payload.set_exception(PayloadAccessError())

            except asyncio.CancelledError:
                self.log_debug('Ignored premature client disconnection ')
                break
            except RuntimeError as exc:
                if self.debug:
                    self.log_exception(
                        'Unhandled runtime exception', exc_info=exc)
                self.force_close()
            except Exception as exc:
                self.log_exception('Unhandled exception', exc_info=exc)
                self.force_close()
            finally:
                if self.transport is None and resp is not None:
                    self.log_debug('Ignored premature client disconnection.')
                elif not self._force_close:
                    if self._keepalive and not self._close:
                        # start keep-alive timer
                        if keepalive_timeout is not None:
                            now = self._loop.time()
                            self._keepalive_time = now
                            if self._keepalive_handle is None:
                                self._keepalive_handle = loop.call_at(
                                    now + keepalive_timeout,
                                    self._process_keepalive)
                    else:
                        break

        # remove handler, close transport if no handlers left
        if not self._force_close:
            self._task_handler = None
            if self.transport is not None and self._error_handler is None:
                self.transport.close()