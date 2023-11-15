def monitor(pid,
            try_id,
            task_id,
            monitoring_hub_url,
            run_id,
            logging_level=logging.INFO,
            sleep_dur=10,
            first_message=False):
    """Internal
    Monitors the Parsl task's resources by pointing psutil to the task's pid and watching it and its children.
    """
    import platform
    import time

    radio = UDPRadio(monitoring_hub_url,
                     source_id=task_id)

    if first_message:
        msg = {'run_id': run_id,
               'task_id': task_id,
               'hostname': platform.node(),
               'first_msg': first_message,
               'timestamp': datetime.datetime.now()
        }
        radio.send(msg)
        return

    import psutil
    import logging

    format_string = "%(asctime)s.%(msecs)03d %(name)s:%(lineno)d [%(levelname)s]  %(message)s"
    logging.basicConfig(filename='{logbase}/monitor.{task_id}.{pid}.log'.format(
        logbase="/tmp", task_id=task_id, pid=pid), level=logging_level, format=format_string)

    logging.debug("start of monitor")

    # these values are simple to log. Other information is available in special formats such as memory below.
    simple = ["cpu_num", 'cpu_percent', 'create_time', 'cwd', 'exe', 'memory_percent', 'nice', 'name', 'num_threads', 'pid', 'ppid', 'status', 'username']
    # values that can be summed up to see total resources used by task process and its children
    summable_values = ['cpu_percent', 'memory_percent', 'num_threads']

    pm = psutil.Process(pid)
    pm.cpu_percent()

    children_user_time = {}
    children_system_time = {}
    total_children_user_time = 0.0
    total_children_system_time = 0.0
    while True:
        logging.debug("start of monitoring loop")
        try:
            d = {"psutil_process_" + str(k): v for k, v in pm.as_dict().items() if k in simple}
            d["run_id"] = run_id
            d["task_id"] = task_id
            d["try_id"] = try_id
            d['resource_monitoring_interval'] = sleep_dur
            d['hostname'] = platform.node()
            d['first_msg'] = first_message
            d['timestamp'] = datetime.datetime.now()

            logging.debug("getting children")
            children = pm.children(recursive=True)
            logging.debug("got children")

            d["psutil_cpu_count"] = psutil.cpu_count()
            d['psutil_process_memory_virtual'] = pm.memory_info().vms
            d['psutil_process_memory_resident'] = pm.memory_info().rss
            d['psutil_process_time_user'] = pm.cpu_times().user
            d['psutil_process_time_system'] = pm.cpu_times().system
            d['psutil_process_children_count'] = len(children)
            try:
                d['psutil_process_disk_write'] = pm.io_counters().write_bytes
                d['psutil_process_disk_read'] = pm.io_counters().read_bytes
            except Exception:
                # occasionally pid temp files that hold this information are unvailable to be read so set to zero
                logging.exception("Exception reading IO counters for main process. Recorded IO usage may be incomplete", exc_info=True)
                d['psutil_process_disk_write'] = 0
                d['psutil_process_disk_read'] = 0
            for child in children:
                for k, v in child.as_dict(attrs=summable_values).items():
                    d['psutil_process_' + str(k)] += v
                child_user_time = child.cpu_times().user
                child_system_time = child.cpu_times().system
                total_children_user_time += child_user_time - children_user_time.get(child.pid, 0)
                total_children_system_time += child_system_time - children_system_time.get(child.pid, 0)
                children_user_time[child.pid] = child_user_time
                children_system_time[child.pid] = child_system_time
                d['psutil_process_memory_virtual'] += child.memory_info().vms
                d['psutil_process_memory_resident'] += child.memory_info().rss
                try:
                    d['psutil_process_disk_write'] += child.io_counters().write_bytes
                    d['psutil_process_disk_read'] += child.io_counters().read_bytes
                except Exception:
                    # occassionally pid temp files that hold this information are unvailable to be read so add zero
                    logging.exception("Exception reading IO counters for child {k}. Recorded IO usage may be incomplete".format(k=k), exc_info=True)
                    d['psutil_process_disk_write'] += 0
                    d['psutil_process_disk_read'] += 0
            d['psutil_process_time_user'] += total_children_user_time
            d['psutil_process_time_system'] += total_children_system_time
            logging.debug("sending message")
            radio.send(d)
        except Exception:
            logging.exception("Exception getting the resource usage. Not sending usage to Hub", exc_info=True)

        logging.debug("sleeping")
        time.sleep(sleep_dur)

    logger.info("Monitor exiting")