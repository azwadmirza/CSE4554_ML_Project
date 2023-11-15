def run_deploy(conanfile, install_folder, output):
    deploy_output = ScopedOutput("%s deploy()" % output.scope, output)
    file_importer = _FileImporter(conanfile, install_folder)
    package_copied = set()

    # This is necessary to capture FileCopier full destination paths
    # Maybe could be improved in FileCopier
    def file_copier(*args, **kwargs):
        file_copy = FileCopier(conanfile.package_folder, install_folder)
        copied = file_copy(*args, **kwargs)
        package_copied.update(copied)

    conanfile.copy_deps = file_importer
    conanfile.copy = file_copier
    conanfile.install_folder = install_folder
    with get_env_context_manager(conanfile):
        with tools.chdir(install_folder):
            conanfile.deploy()

    copied_files = file_importer.copied_files
    copied_files.update(package_copied)
    _report_save_manifest(copied_files, deploy_output, install_folder, "deploy_manifest.txt")