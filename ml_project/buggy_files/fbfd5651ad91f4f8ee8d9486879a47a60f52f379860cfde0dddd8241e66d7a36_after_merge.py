    def wrapped(self, *args, **kwargs):
        remaining_tries = int(C.ANSIBLE_SSH_RETRIES) + 1
        cmd_summary = u"%s..." % to_text(args[0])
        for attempt in range(remaining_tries):
            cmd = args[0]
            if attempt != 0 and self._play_context.password and isinstance(cmd, list):
                # If this is a retry, the fd/pipe for sshpass is closed, and we need a new one
                self.sshpass_pipe = os.pipe()
                cmd[1] = b'-d' + to_bytes(self.sshpass_pipe[0], nonstring='simplerepr', errors='surrogate_or_strict')

            try:
                try:
                    return_tuple = func(self, *args, **kwargs)
                    if self._play_context.no_log:
                        display.vvv(u'rc=%s, stdout and stderr censored due to no log' % return_tuple[0], host=self.host)
                    else:
                        display.vvv(return_tuple, host=self.host)
                    # 0 = success
                    # 1-254 = remote command return code
                    # 255 could be a failure from the ssh command itself
                except (AnsibleControlPersistBrokenPipeError):
                    # Retry one more time because of the ControlPersist broken pipe (see #16731)
                    cmd = args[0]
                    if self._play_context.password and isinstance(cmd, list):
                        # This is a retry, so the fd/pipe for sshpass is closed, and we need a new one
                        self.sshpass_pipe = os.pipe()
                        cmd[1] = b'-d' + to_bytes(self.sshpass_pipe[0], nonstring='simplerepr', errors='surrogate_or_strict')
                    display.vvv(u"RETRYING BECAUSE OF CONTROLPERSIST BROKEN PIPE")
                    return_tuple = func(self, *args, **kwargs)

                remaining_retries = remaining_tries - attempt - 1
                _handle_error(remaining_retries, cmd[0], return_tuple, self._play_context.no_log, self.host)

                break

            # 5 = Invalid/incorrect password from sshpass
            except AnsibleAuthenticationFailure:
                # Raising this exception, which is subclassed from AnsibleConnectionFailure, prevents further retries
                raise

            except (AnsibleConnectionFailure, Exception) as e:

                if attempt == remaining_tries - 1:
                    raise
                else:
                    pause = 2 ** attempt - 1
                    if pause > 30:
                        pause = 30

                    if isinstance(e, AnsibleConnectionFailure):
                        msg = u"ssh_retry: attempt: %d, ssh return code is 255. cmd (%s), pausing for %d seconds" % (attempt + 1, cmd_summary, pause)
                    else:
                        msg = (u"ssh_retry: attempt: %d, caught exception(%s) from cmd (%s), "
                               u"pausing for %d seconds" % (attempt + 1, to_text(e), cmd_summary, pause))

                    display.vv(msg, host=self.host)

                    time.sleep(pause)
                    continue

        return return_tuple