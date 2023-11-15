    def wait_until_status(self, pxname, svname, status):
        """
        Wait for a service to reach the specified status. Try RETRIES times
        with INTERVAL seconds of sleep in between. If the service has not reached
        the expected status in that time, the module will fail. If the service was
        not found, the module will fail.
        """
        for i in range(1, self.wait_retries):
            state = self.get_state_for(pxname, svname)

            # We can assume there will only be 1 element in state because both svname and pxname are always set when we get here
            if state[0]['status'] == status:
                if not self._drain or (state[0]['scur'] == '0' and state == 'MAINT'):
                    return True
            else:
                time.sleep(self.wait_interval)

        self.module.fail_json(msg="server %s/%s not status '%s' after %d retries. Aborting." %
                              (pxname, svname, status, self.wait_retries))