def extract_layer_tar(layer_tar_path, directory_path):
    '''Assuming all the metadata for an image has been extracted into the
    temp folder, extract the tarfile into the required directory'''
    os.makedirs(directory_path)
    with open(os.devnull, 'w') as test:
        result = subprocess.call(['tar', '-tf', layer_tar_path],
                                 stdout=test, stderr=test)
    if not result:
        root_command(extract_tar, layer_tar_path, '-C', directory_path)