def export_conanfile(output, paths, conanfile, origin_folder, conan_ref, keep_source):
    destination_folder = paths.export(conan_ref)
    previous_digest = _init_export_folder(destination_folder)
    execute_export(conanfile, origin_folder, destination_folder, output)

    digest = FileTreeManifest.create(destination_folder)
    save(os.path.join(destination_folder, CONAN_MANIFEST), str(digest))

    if previous_digest and previous_digest == digest:
        digest = previous_digest
        output.info("The stored package has not changed")
        modified_recipe = False
    else:
        output.success('A new %s version was exported' % CONANFILE)
        output.info('Folder: %s' % destination_folder)
        modified_recipe = True

    source = paths.source(conan_ref, conanfile.short_paths)
    dirty = os.path.join(source, DIRTY_FILE)
    remove = False
    if os.path.exists(dirty):
        output.info("Source folder is dirty, forcing removal")
        remove = True
    elif modified_recipe and not keep_source and os.path.exists(source):
        output.info("Package recipe modified in export, forcing source folder removal")
        output.info("Use the --keep-source, -k option to skip it")
        remove = True
    if remove:
        output.info("Removing 'source' folder, this can take a while for big packages")
        try:
            # remove only the internal
            rmdir(source)
        except BaseException as e:
            output.error("Unable to delete source folder. "
                         "Will be marked as dirty for deletion")
            output.warn(str(e))
            save(os.path.join(source, DIRTY_FILE), "")