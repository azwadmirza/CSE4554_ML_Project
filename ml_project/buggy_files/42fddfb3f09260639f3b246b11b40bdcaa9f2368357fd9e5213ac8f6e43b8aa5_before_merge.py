def register_env(location):
    location = normpath(location)

    if "placehold_pl" in location:
        # Don't record envs created by conda-build.
        return

    if location in yield_lines(USER_ENVIRONMENTS_TXT_FILE):
        # Nothing to do. Location is already recorded in a known environments.txt file.
        return

    with open(USER_ENVIRONMENTS_TXT_FILE, 'a') as fh:
        fh.write(location)
        fh.write('\n')