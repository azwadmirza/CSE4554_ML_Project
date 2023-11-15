def _build_collection_tar(b_collection_path, b_tar_path, collection_manifest, file_manifest):
    files_manifest_json = to_bytes(json.dumps(file_manifest, indent=True), errors='surrogate_or_strict')
    collection_manifest['file_manifest_file']['chksum_sha256'] = secure_hash_s(files_manifest_json, hash_func=sha256)
    collection_manifest_json = to_bytes(json.dumps(collection_manifest, indent=True), errors='surrogate_or_strict')

    with _tempdir() as b_temp_path:
        b_tar_filepath = os.path.join(b_temp_path, os.path.basename(b_tar_path))

        with tarfile.open(b_tar_filepath, mode='w:gz') as tar_file:
            # Add the MANIFEST.json and FILES.json file to the archive
            for name, b in [('MANIFEST.json', collection_manifest_json), ('FILES.json', files_manifest_json)]:
                b_io = BytesIO(b)
                tar_info = tarfile.TarInfo(name)
                tar_info.size = len(b)
                tar_info.mtime = time.time()
                tar_info.mode = 0o0644
                tar_file.addfile(tarinfo=tar_info, fileobj=b_io)

            for file_info in file_manifest['files']:
                if file_info['name'] == '.':
                    continue

                # arcname expects a native string, cannot be bytes
                filename = to_native(file_info['name'], errors='surrogate_or_strict')
                b_src_path = os.path.join(b_collection_path, to_bytes(filename, errors='surrogate_or_strict'))

                def reset_stat(tarinfo):
                    existing_is_exec = tarinfo.mode & stat.S_IXUSR
                    tarinfo.mode = 0o0755 if existing_is_exec or tarinfo.isdir() else 0o0644
                    tarinfo.uid = tarinfo.gid = 0
                    tarinfo.uname = tarinfo.gname = ''
                    return tarinfo

                tar_file.add(os.path.realpath(b_src_path), arcname=filename, recursive=False, filter=reset_stat)

        shutil.copy(b_tar_filepath, b_tar_path)
        collection_name = "%s.%s" % (collection_manifest['collection_info']['namespace'],
                                     collection_manifest['collection_info']['name'])
        display.display('Created collection for %s at %s' % (collection_name, to_text(b_tar_path)))