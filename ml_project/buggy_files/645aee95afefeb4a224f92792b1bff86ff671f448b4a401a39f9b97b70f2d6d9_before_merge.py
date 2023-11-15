    def file_copier(*args, **kwargs):
        file_copy = FileCopier(conanfile.package_folder, install_folder)
        copied = file_copy(*args, **kwargs)
        package_copied.update(copied)