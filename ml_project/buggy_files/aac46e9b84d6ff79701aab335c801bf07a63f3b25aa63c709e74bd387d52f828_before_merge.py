def clean_old_jobs():
    '''
    Clean out the old jobs from the job cache
    '''
    if __opts__['keep_jobs'] != 0:
        cur = time.time()
        jid_root = _job_dir()

        if not os.path.exists(jid_root):
            return

        for top in os.listdir(jid_root):
            t_path = os.path.join(jid_root, top)
            for final in os.listdir(t_path):
                f_path = os.path.join(t_path, final)
                jid_file = os.path.join(f_path, 'jid')
                if not os.path.isfile(jid_file):
                    # No jid file means corrupted cache entry, scrub it
                    shutil.rmtree(f_path)
                else:
                    jid_ctime = os.stat(jid_file).st_ctime
                    hours_difference = (cur - jid_ctime) / 3600.0
                    if hours_difference > __opts__['keep_jobs']:
                        shutil.rmtree(f_path)