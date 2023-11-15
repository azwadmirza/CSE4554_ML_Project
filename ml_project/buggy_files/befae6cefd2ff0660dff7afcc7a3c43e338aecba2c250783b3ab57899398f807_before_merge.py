def undo_imports(current_path, output):
    manifest_path = os.path.join(current_path, IMPORTS_MANIFESTS)
    try:
        manifest_content = load(manifest_path)
    except:
        raise ConanException("Cannot load file %s" % manifest_path)

    try:
        manifest = FileTreeManifest.loads(manifest_content)
    except:
        raise ConanException("Wrong manifest file format %s" % manifest_path)

    not_removed = 0
    for filepath, _ in manifest.file_sums.items():
        if not os.path.exists(filepath):
            output.warn("File doesn't exist: %s" % filepath)
            continue
        try:
            os.remove(filepath)
        except:
            output.error("Cannot remove file (open or busy): %s" % filepath)
            not_removed += 1

    if not_removed:
        raise ConanException("Cannot remove %s or more imported files" % not_removed)

    output.success("Removed %s imported files" % (len(manifest.file_sums)))
    try:
        os.remove(manifest_path)
        output.success("Removed imports manifest file: %s" % manifest_path)
    except:
        raise ConanException("Cannot remove manifest file (open or busy): %s" % manifest_path)