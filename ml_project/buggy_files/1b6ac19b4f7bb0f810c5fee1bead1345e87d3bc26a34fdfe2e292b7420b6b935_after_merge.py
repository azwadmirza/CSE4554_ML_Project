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