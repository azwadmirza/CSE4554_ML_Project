    def from_tar(b_path, force, parent=None):
        if not tarfile.is_tarfile(b_path):
            raise AnsibleError("Collection artifact at '%s' is not a valid tar file." % to_native(b_path))

        info = {}
        with tarfile.open(b_path, mode='r') as collection_tar:
            for b_member_name, property_name in CollectionRequirement._FILE_MAPPING:
                n_member_name = to_native(b_member_name)
                try:
                    member = collection_tar.getmember(n_member_name)
                except KeyError:
                    raise AnsibleError("Collection at '%s' does not contain the required file %s."
                                       % (to_native(b_path), n_member_name))

                with _tarfile_extract(collection_tar, member) as (dummy, member_obj):
                    try:
                        info[property_name] = json.loads(to_text(member_obj.read(), errors='surrogate_or_strict'))
                    except ValueError:
                        raise AnsibleError("Collection tar file member %s does not contain a valid json string."
                                           % n_member_name)

        meta = info['manifest_file']['collection_info']
        files = info['files_file']['files']

        namespace = meta['namespace']
        name = meta['name']
        version = meta['version']
        meta = CollectionVersionMetadata(namespace, name, version, None, None, meta['dependencies'])

        return CollectionRequirement(namespace, name, b_path, None, [version], version, force, parent=parent,
                                     metadata=meta, files=files)