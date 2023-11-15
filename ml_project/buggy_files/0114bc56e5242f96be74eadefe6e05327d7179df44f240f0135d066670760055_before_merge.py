def _wait_for_task(task, vm_name, task_type, sleep_seconds=1, log_level='debug'):
    time_counter = 0
    while task.info.state == 'running':
        message = "[ {0} ] Waiting for {1} task to finish [{2} s]".format(vm_name, task_type, time_counter)
        if log_level == 'info':
            log.info(message)
        else:
            log.debug(message)
        time.sleep(int(sleep_seconds))
        time_counter += int(sleep_seconds)
    if task.info.state == 'success':
        message = "[ {0} ] Successfully completed {1} task in {2} seconds".format(vm_name, task_type, time_counter)
        if log_level == 'info':
            log.info(message)
        else:
            log.debug(message)
    else:
        raise task.info.error