def load_extension_images_thru_services(cli_ctx, publisher, name, version, location,
                                        show_latest=False, partial_match=True):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from distutils.version import LooseVersion  # pylint: disable=no-name-in-module,import-error
    all_images = []
    client = _compute_client_factory(cli_ctx)
    if location is None:
        location = get_one_of_subscription_locations(cli_ctx)

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

    publishers = client.virtual_machine_images.list_publishers(location)
    if publisher:
        publishers = [p for p in publishers if _matched(publisher, p.name, partial_match)]

    publisher_num = len(publishers)
    if publisher_num > 1:
        with ThreadPoolExecutor(max_workers=_get_thread_count()) as executor:
            tasks = [executor.submit(_load_extension_images_from_publisher,
                                     p.name) for p in publishers]
            for t in as_completed(tasks):
                t.result()  # don't use the result but expose exceptions from the threads
    elif publisher_num == 1:
        _load_extension_images_from_publisher(publishers[0].name)

    return all_images