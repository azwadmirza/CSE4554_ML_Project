def get_recording_dirs(data_dir):
    '''
        You can supply a data folder or any folder
        - all folders within will be checked for necessary files
        - in order to make a visualization
    '''
    filtered_recording_dirs = []
    if is_pupil_rec_dir(data_dir):
        filtered_recording_dirs.append(data_dir)
    for root, dirs, files in os.walk(data_dir):
        filtered_recording_dirs += [os.path.join(root, d) for d in dirs
                                    if not d.startswith(".") and is_pupil_rec_dir(os.path.join(root, d))]
    logger.debug("Filtered Recording Dirs: {}".format(filtered_recording_dirs))
    return filtered_recording_dirs