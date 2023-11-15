    def wait_for_monit_to_stop_pending():
        """Fails this run if there is no status or it's pending/initializing for timeout"""
        timeout_time = time.time() + timeout
        sleep_time = 5

        running_status = status()
        while running_status == '' or 'pending' in running_status or 'initializing' in running_status:
            if time.time() >= timeout_time:
                module.fail_json(
                    msg='waited too long for "pending", or "initiating" status to go away ({0})'.format(
                        running_status
                    ),
                    state=state
                )

            time.sleep(sleep_time)
            running_status = status()