def add_job(info):
    """Add a new job to the jobs dictionary."""
    num = get_next_job_number()
    info['started'] = time.time()
    info['status'] = "running"
    _set_pgrp(info)
    tasks.appendleft(num)
    builtins.__xonsh_all_jobs__[num] = info
    if info['bg']:
        print_one_job(num)