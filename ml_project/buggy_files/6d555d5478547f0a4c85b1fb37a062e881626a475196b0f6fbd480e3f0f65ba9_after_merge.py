def get_working_dir():
    '''General purpose utility to return the absolute path of the working
    directory'''
    return os.path.join(mount_dir, constants.temp_folder)