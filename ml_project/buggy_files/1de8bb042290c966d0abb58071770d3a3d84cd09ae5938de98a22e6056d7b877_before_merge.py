def cleanup_noncompliant_channel_torrents(state_dir):
    channels_dir = os.path.join(state_dir, "channels")
    # Remove torrents contents
    if os.path.exists(channels_dir):
        for d in os.listdir(channels_dir):
            if len(os.path.splitext(d)[0]) != CHANNEL_DIR_NAME_LENGTH:
                dir_path = os.path.join(channels_dir, d)
                # We remove both malformed channel dirs and .torrent and .mdblob files for personal channel
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path, ignore_errors=True)
                elif os.path.isfile(dir_path):
                    os.unlink(dir_path)

    # Remove .state torrent resume files
    resume_dir = os.path.join(state_dir, "dlcheckpoints")
    if os.path.exists(resume_dir):
        for f in os.listdir(resume_dir):
            file_path = os.path.join(resume_dir, f)
            pstate = CallbackConfigParser()
            pstate.read_file(file_path)

            if pstate and pstate.has_option('download_defaults', 'channel_download') and \
                    pstate.get('download_defaults', 'channel_download'):
                try:
                    name = pstate.get('state', 'metainfo')['info']['name']
                    if name and len(name) != CHANNEL_DIR_NAME_LENGTH:
                        os.unlink(file_path)
                except (TypeError, KeyError, ValueError):
                    pass