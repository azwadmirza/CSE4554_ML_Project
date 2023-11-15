    def _finalize(self, why, terminate_debuggee):
        # If the IDE started a session, and then disconnected before issuing "launch"
        # or "attach", the main thread will be blocked waiting for the first server
        # connection to come in - unblock it, so that we can exit.
        servers.dont_wait_for_first_connection()

        if self.server:
            if self.server.is_connected:
                if terminate_debuggee and self.launcher and self.launcher.is_connected:
                    # If we were specifically asked to terminate the debuggee, and we
                    # can ask the launcher to kill it, do so instead of disconnecting
                    # from the server to prevent debuggee from running any more code.
                    self.launcher.terminate_debuggee()
                else:
                    # Otherwise, let the server handle it the best it can.
                    try:
                        self.server.channel.request(
                            "disconnect", {"terminateDebuggee": terminate_debuggee}
                        )
                    except Exception:
                        pass
            self.server.detach_from_session()

        if self.launcher and self.launcher.is_connected:
            # If there was a server, we just disconnected from it above, which should
            # cause the debuggee process to exit - so let's wait for that first.
            if self.server:
                log.info('{0} waiting for "exited" event...', self)
                if not self.wait_for(
                    lambda: self.launcher.exit_code is not None, timeout=5
                ):
                    log.warning('{0} timed out waiting for "exited" event.', self)

            # Terminate the debuggee process if it's still alive for any reason -
            # whether it's because there was no server to handle graceful shutdown,
            # or because the server couldn't handle it for some reason.
            self.launcher.terminate_debuggee()

            # Wait until the launcher message queue fully drains. There is no timeout
            # here, because the final "terminated" event will only come after reading
            # user input in wait-on-exit scenarios.
            log.info("{0} waiting for {1} to disconnect...", self, self.launcher)
            self.wait_for(lambda: not self.launcher.is_connected)

            try:
                self.launcher.channel.close()
            except Exception:
                log.exception()

        if self.ide:
            if self.ide.is_connected:
                # Tell the IDE that debugging is over, but don't close the channel until it
                # tells us to, via the "disconnect" request.
                try:
                    self.ide.channel.send_event("terminated")
                except Exception:
                    pass

            if self.ide.start_request is not None and self.ide.start_request.command == "launch":
                servers.stop_listening()
                log.info('"launch" session ended - killing remaining debuggee processes.')

                pids_killed = set()
                if self.launcher and self.launcher.pid is not None:
                    # Already killed above.
                    pids_killed.add(self.launcher.pid)

                while True:
                    conns = [conn for conn in servers.connections() if conn.pid not in pids_killed]
                    if not len(conns):
                        break
                    for conn in conns:
                        log.info("Killing {0}", conn)
                        try:
                            os.kill(conn.pid, signal.SIGTERM)
                        except Exception:
                            log.exception("Failed to kill {0}", conn)
                        pids_killed.add(conn.pid)