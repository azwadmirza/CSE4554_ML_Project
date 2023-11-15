    def file_copier(*args, **kwargs):
        file_copy = FileCopier(conanfile.package_folder, install_folder)
        copied = file_copy(*args, **kwargs)
        _make_files_writable(copied)
        package_copied.update(copied)