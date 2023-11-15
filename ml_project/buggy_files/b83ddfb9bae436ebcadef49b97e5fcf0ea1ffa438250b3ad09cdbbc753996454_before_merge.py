def extract_layer_tar(layer_tar_path, directory_path):
    '''Assuming all the metadata for an image has been extracted into the
    temp folder, extract the tarfile into the required directory'''
    with tarfile.open(layer_tar_path) as tar:
        tar.extractall(directory_path)