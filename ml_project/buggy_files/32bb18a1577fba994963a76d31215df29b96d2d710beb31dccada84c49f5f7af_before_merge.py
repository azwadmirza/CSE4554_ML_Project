def clean_working_dir(bind_mount):
    '''Clean up the working directory
    If bind_mount is true then leave the upper level directory'''
    path = rootfs.get_working_dir()
    if os.path.exists(path):
        if bind_mount:
            # clean whatever is in temp_folder without removing the folder
            inodes = os.listdir(path)
            for inode in inodes:
                dir_path = os.path.join(path, inode)
                if os.path.isdir(dir_path):
                    shutil.rmtree(dir_path)
                else:
                    os.remove(dir_path)
        else:
            shutil.rmtree(path)