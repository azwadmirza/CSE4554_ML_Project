    async def spawn_single_user(self, user, server_name='', options=None):
        # in case of error, include 'try again from /hub/home' message
        if self.authenticator.refresh_pre_spawn:
            auth_user = await self.refresh_auth(user, force=True)
            if auth_user is None:
                raise web.HTTPError(
                    403, "auth has expired for %s, login again", user.name
                )

        spawn_start_time = time.perf_counter()
        self.extra_error_html = self.spawn_home_error

        user_server_name = user.name

        if server_name:
            user_server_name = '%s:%s' % (user.name, server_name)

        if server_name in user.spawners and user.spawners[server_name].pending:
            pending = user.spawners[server_name].pending
            SERVER_SPAWN_DURATION_SECONDS.labels(
                status=ServerSpawnStatus.already_pending
            ).observe(time.perf_counter() - spawn_start_time)
            raise RuntimeError("%s pending %s" % (user_server_name, pending))

        # count active servers and pending spawns
        # we could do careful bookkeeping to avoid
        # but for 10k users this takes ~5ms
        # and saves us from bookkeeping errors
        active_counts = self.users.count_active_users()
        spawn_pending_count = (
            active_counts['spawn_pending'] + active_counts['proxy_pending']
        )
        active_count = active_counts['active']
        RUNNING_SERVERS.set(active_count)

        concurrent_spawn_limit = self.concurrent_spawn_limit
        active_server_limit = self.active_server_limit

        if concurrent_spawn_limit and spawn_pending_count >= concurrent_spawn_limit:
            SERVER_SPAWN_DURATION_SECONDS.labels(
                status=ServerSpawnStatus.throttled
            ).observe(time.perf_counter() - spawn_start_time)
            # Suggest number of seconds client should wait before retrying
            # This helps prevent thundering herd problems, where users simply
            # immediately retry when we are overloaded.
            retry_range = self.settings['spawn_throttle_retry_range']
            retry_time = int(random.uniform(*retry_range))

            # round suggestion to nicer human value (nearest 10 seconds or minute)
            if retry_time <= 90:
                # round human seconds up to nearest 10
                human_retry_time = "%i0 seconds" % math.ceil(retry_time / 10.0)
            else:
                # round number of minutes
                human_retry_time = "%i minutes" % math.round(retry_time / 60.0)

            self.log.warning(
                '%s pending spawns, throttling. Suggested retry in %s seconds.',
                spawn_pending_count,
                retry_time,
            )
            err = web.HTTPError(
                429,
                "Too many users trying to log in right now. Try again in {}.".format(
                    human_retry_time
                ),
            )
            # can't call set_header directly here because it gets ignored
            # when errors are raised
            # we handle err.headers ourselves in Handler.write_error
            err.headers = {'Retry-After': retry_time}
            raise err

        if active_server_limit and active_count >= active_server_limit:
            self.log.info('%s servers active, no space available', active_count)
            SERVER_SPAWN_DURATION_SECONDS.labels(
                status=ServerSpawnStatus.too_many_users
            ).observe(time.perf_counter() - spawn_start_time)
            raise web.HTTPError(
                429, "Active user limit exceeded. Try again in a few minutes."
            )

        tic = IOLoop.current().time()

        self.log.debug("Initiating spawn for %s", user_server_name)

        spawn_future = user.spawn(server_name, options, handler=self)

        self.log.debug(
            "%i%s concurrent spawns",
            spawn_pending_count,
            '/%i' % concurrent_spawn_limit if concurrent_spawn_limit else '',
        )
        self.log.debug(
            "%i%s active servers",
            active_count,
            '/%i' % active_server_limit if active_server_limit else '',
        )

        spawner = user.spawners[server_name]
        # set spawn_pending now, so there's no gap where _spawn_pending is False
        # while we are waiting for _proxy_pending to be set
        spawner._spawn_pending = True

        async def finish_user_spawn():
            """Finish the user spawn by registering listeners and notifying the proxy.

            If the spawner is slow to start, this is passed as an async callback,
            otherwise it is called immediately.
            """
            # wait for spawn Future
            await spawn_future
            toc = IOLoop.current().time()
            self.log.info(
                "User %s took %.3f seconds to start", user_server_name, toc - tic
            )
            self.statsd.timing('spawner.success', (toc - tic) * 1000)
            SERVER_SPAWN_DURATION_SECONDS.labels(
                status=ServerSpawnStatus.success
            ).observe(time.perf_counter() - spawn_start_time)
            self.eventlog.record_event(
                'hub.jupyter.org/server-action',
                1,
                {'action': 'start', 'username': user.name, 'servername': server_name},
            )
            proxy_add_start_time = time.perf_counter()
            spawner._proxy_pending = True
            try:
                await self.proxy.add_user(user, server_name)

                PROXY_ADD_DURATION_SECONDS.labels(status='success').observe(
                    time.perf_counter() - proxy_add_start_time
                )
                RUNNING_SERVERS.inc()
            except Exception:
                self.log.exception("Failed to add %s to proxy!", user_server_name)
                self.log.error(
                    "Stopping %s to avoid inconsistent state", user_server_name
                )
                await user.stop(server_name)
                PROXY_ADD_DURATION_SECONDS.labels(status='failure').observe(
                    time.perf_counter() - proxy_add_start_time
                )
            else:
                spawner.add_poll_callback(self.user_stopped, user, server_name)
            finally:
                spawner._proxy_pending = False

        # hook up spawner._spawn_future so that other requests can await
        # this result
        finish_spawn_future = spawner._spawn_future = maybe_future(finish_user_spawn())

        def _clear_spawn_future(f):
            # clear spawner._spawn_future when it's done
            # keep an exception around, though, to prevent repeated implicit spawns
            # if spawn is failing
            if f.cancelled() or f.exception() is None:
                spawner._spawn_future = None
            # Now we're all done. clear _spawn_pending flag
            spawner._spawn_pending = False

        finish_spawn_future.add_done_callback(_clear_spawn_future)

        # when spawn finishes (success or failure)
        # update failure count and abort if consecutive failure limit
        # is reached
        def _track_failure_count(f):
            if f.cancelled() or f.exception() is None:
                # spawn succeeded, reset failure count
                self.settings['failure_count'] = 0
                return
            # spawn failed, increment count and abort if limit reached
            self.settings.setdefault('failure_count', 0)
            self.settings['failure_count'] += 1
            failure_count = self.settings['failure_count']
            failure_limit = spawner.consecutive_failure_limit
            if failure_limit and 1 < failure_count < failure_limit:
                self.log.warning(
                    "%i consecutive spawns failed.  "
                    "Hub will exit if failure count reaches %i before succeeding",
                    failure_count,
                    failure_limit,
                )
            if failure_limit and failure_count >= failure_limit:
                self.log.critical(
                    "Aborting due to %i consecutive spawn failures", failure_count
                )
                # abort in 2 seconds to allow pending handlers to resolve
                # mostly propagating errors for the current failures
                def abort():
                    raise SystemExit(1)

                IOLoop.current().call_later(2, abort)

        finish_spawn_future.add_done_callback(_track_failure_count)

        try:
            await gen.with_timeout(
                timedelta(seconds=self.slow_spawn_timeout), finish_spawn_future
            )
        except gen.TimeoutError:
            # waiting_for_response indicates server process has started,
            # but is yet to become responsive.
            if spawner._spawn_pending and not spawner._waiting_for_response:
                # still in Spawner.start, which is taking a long time
                # we shouldn't poll while spawn is incomplete.
                self.log.warning(
                    "User %s is slow to start (timeout=%s)",
                    user_server_name,
                    self.slow_spawn_timeout,
                )
                return

            # start has finished, but the server hasn't come up
            # check if the server died while we were waiting
            poll_start_time = time.perf_counter()
            status = await spawner.poll()
            SERVER_POLL_DURATION_SECONDS.labels(
                status=ServerPollStatus.from_status(status)
            ).observe(time.perf_counter() - poll_start_time)

            if status is not None:
                toc = IOLoop.current().time()
                self.statsd.timing('spawner.failure', (toc - tic) * 1000)
                SERVER_SPAWN_DURATION_SECONDS.labels(
                    status=ServerSpawnStatus.failure
                ).observe(time.perf_counter() - spawn_start_time)

                raise web.HTTPError(
                    500,
                    "Spawner failed to start [status=%s]. The logs for %s may contain details."
                    % (status, spawner._log_name),
                )

            if spawner._waiting_for_response:
                # hit timeout waiting for response, but server's running.
                # Hope that it'll show up soon enough,
                # though it's possible that it started at the wrong URL
                self.log.warning(
                    "User %s is slow to become responsive (timeout=%s)",
                    user_server_name,
                    self.slow_spawn_timeout,
                )
                self.log.debug(
                    "Expecting server for %s at: %s",
                    user_server_name,
                    spawner.server.url,
                )
            if spawner._proxy_pending:
                # User.spawn finished, but it hasn't been added to the proxy
                # Could be due to load or a slow proxy
                self.log.warning(
                    "User %s is slow to be added to the proxy (timeout=%s)",
                    user_server_name,
                    self.slow_spawn_timeout,
                )