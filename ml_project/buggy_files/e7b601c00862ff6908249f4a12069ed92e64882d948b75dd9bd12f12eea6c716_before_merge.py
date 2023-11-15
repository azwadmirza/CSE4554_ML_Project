def run_imports(conanfile, dest_folder, output):
    if not hasattr(conanfile, "imports"):
        return []
    file_importer = _FileImporter(conanfile, dest_folder)
    conanfile.copy = file_importer
    conanfile.imports_folder = dest_folder
    with get_env_context_manager(conanfile):
        with tools.chdir(dest_folder):
            conanfile.imports()
    copied_files = file_importer.copied_files
    import_output = ScopedOutput("%s imports()" % output.scope, output)
    _report_save_manifest(copied_files, import_output, dest_folder, IMPORTS_MANIFESTS)
    return copied_files