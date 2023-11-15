def get_recording_dirs(data_dir):
    '''
        You can supply a data folder or any folder
        - all folders within will be checked for necessary files
        - in order to make a visualization
    '''
    if is_pupil_rec_dir(data_dir):
        yield data_dir
    for root, dirs, files in os.walk(data_dir):
        for d in dirs:
            joined = os.path.join(root, d)
            if not d.startswith(".") and is_pupil_rec_dir(joined):
                yield joined