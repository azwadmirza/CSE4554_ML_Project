def _package_conf_file_to_dir(file_name):
    '''
    Convert a config file to a config directory.
    '''
    if file_name in SUPPORTED_CONFS:
        path = BASE_PATH.format(file_name)
        if os.path.exists(path):
            if os.path.isdir(path):
                return False
            else:
                os.rename(path, path + '.tmpbak')
                os.mkdir(path, 0o755)
                os.rename(path + '.tmpbak', os.path.join(path, 'tmp'))
                return True
        else:
            os.mkdir(path, 0o755)
            return True