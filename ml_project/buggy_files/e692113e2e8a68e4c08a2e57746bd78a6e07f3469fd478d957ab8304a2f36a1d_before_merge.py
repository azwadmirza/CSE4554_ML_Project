    def _load_extension_images_from_publisher(publisher):
        from msrestazure.azure_exceptions import CloudError
        try:
            types = client.virtual_machine_extension_images.list_types(location, publisher)
        except CloudError:  # PIR image publishers might not have any extension images, exception could raise
            types = []
        if name:
            types = [t for t in types if _matched(name, t.name, partial_match)]
        for t in types:
            versions = client.virtual_machine_extension_images.list_versions(location,
                                                                             publisher,
                                                                             t.name)
            if version:
                versions = [v for v in versions if _matched(version, v.name, partial_match)]

            if show_latest:
                # pylint: disable=no-member
                versions.sort(key=lambda v: LooseVersion(v.name), reverse=True)
                all_images.append({
                    'publisher': publisher,
                    'name': t.name,
                    'version': versions[0].name})
            else:
                for v in versions:
                    all_images.append({
                        'publisher': publisher,
                        'name': t.name,
                        'version': v.name})