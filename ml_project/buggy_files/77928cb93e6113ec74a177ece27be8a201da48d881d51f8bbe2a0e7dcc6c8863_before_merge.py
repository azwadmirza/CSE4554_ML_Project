def _tarfile_extract(tar, member):
    tar_obj = tar.extractfile(member)
    yield tar_obj
    tar_obj.close()