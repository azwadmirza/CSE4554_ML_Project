def calc_fs_hash(fs_path):
    '''Given the path to the filesystem, calculate the filesystem hash
    We run a shell script located in the tools directory to get the
    file stats and the file content's sha256sum. We then calculate the
    sha256sum of the contents and write the contents in the layer
    directory.
    Note that this file will be deleted if the -k flag is not given'''
    try:
        hash_contents = subprocess.check_output(
            ['sudo', './tools/fs_hash.sh', os.path.abspath(fs_path)])
        file_name = hashlib.sha256(hash_contents).hexdigest()
        # write file to an appropriate location
        hash_file = os.path.join(os.path.dirname(fs_path), file_name) + '.txt'
        with open(hash_file, 'w') as f:
            f.write(hash_contents.decode('utf-8'))
        return file_name
    except:
        raise