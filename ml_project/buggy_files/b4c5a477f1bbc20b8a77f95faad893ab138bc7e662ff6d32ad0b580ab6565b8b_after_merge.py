    def _send_initial_data(self, fh, in_data, ssh_process):
        '''
        Writes initial data to the stdin filehandle of the subprocess and closes
        it. (The handle must be closed; otherwise, for example, "sftp -b -" will
        just hang forever waiting for more commands.)
        '''

        display.debug(u'Sending initial data')

        try:
            fh.write(to_bytes(in_data))
            fh.close()
        except (OSError, IOError) as e:
            # The ssh connection may have already terminated at this point, with a more useful error
            # Only raise AnsibleConnectionFailure if the ssh process is still alive
            time.sleep(0.001)
            ssh_process.poll()
            if getattr(ssh_process, 'returncode', None) is None:
                raise AnsibleConnectionFailure(
                    'Data could not be sent to remote host "%s". Make sure this host can be reached '
                    'over ssh: %s' % (self.host, to_native(e)), orig_exc=e
                )

        display.debug(u'Sent initial data (%d bytes)' % len(in_data))