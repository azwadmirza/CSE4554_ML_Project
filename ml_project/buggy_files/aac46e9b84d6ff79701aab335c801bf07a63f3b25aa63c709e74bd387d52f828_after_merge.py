def clean_old_jobs():
    '''
    Clean out the old jobs from the job cache
    '''
    if __opts__['keep_jobs'] != 0:
        cur = time.time()
        jid_root = _job_dir()

        if not os.path.exists(jid_root):
            return

        # Keep track of any empty t_path dirs that need to be removed later
        dirs_to_remove = set()

        for top in os.listdir(jid_root):
            t_path = os.path.join(jid_root, top)

            # Check if there are any stray/empty JID t_path dirs
            t_path_dirs = os.listdir(t_path)
            if not t_path_dirs and t_path not in dirs_to_remove:
                dirs_to_remove.add(t_path)
                continue

            for final in t_path_dirs:
                f_path = os.path.join(t_path, final)
                jid_file = os.path.join(f_path, 'jid')
                if not os.path.isfile(jid_file):
                    # No jid file means corrupted cache entry, scrub it
                    # by removing the entire t_path directory
                    shutil.rmtree(t_path)
                else:
                    jid_ctime = os.stat(jid_file).st_ctime
                    hours_difference = (cur - jid_ctime) / 3600.0
                    if hours_difference > __opts__['keep_jobs']:
                        # Remove the entire t_path from the original JID dir
                        shutil.rmtree(t_path)

        # Remove empty JID dirs from job cache, if they're old enough.
        # JID dirs may be empty either from a previous cache-clean with the bug
        # Listed in #29286 still present, or the JID dir was only recently made
        # And the jid file hasn't been created yet.
        if dirs_to_remove:
            for t_path in dirs_to_remove:
                # Checking the time again prevents a possible race condition where
                # t_path JID dirs were created, but not yet populated by a jid file.
                t_path_ctime = os.stat(t_path).st_ctime
                hours_difference = (cur - t_path_ctime) / 3600.0
                if hours_difference > __opts__['keep_jobs']:
                    shutil.rmtree(t_path)