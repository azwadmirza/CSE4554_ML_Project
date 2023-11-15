def download_collections(collections, output_path, apis, validate_certs, no_deps, allow_pre_release):
    """Download Ansible collections as their tarball from a Galaxy server to the path specified and creates a requirements
    file of the downloaded requirements to be used for an install.

    :param collections: The collections to download, should be a list of tuples with (name, requirement, Galaxy Server).
    :param output_path: The path to download the collections to.
    :param apis: A list of GalaxyAPIs to query when search for a collection.
    :param validate_certs: Whether to validate the certificate if downloading a tarball from a non-Galaxy host.
    :param no_deps: Ignore any collection dependencies and only download the base requirements.
    :param allow_pre_release: Do not ignore pre-release versions when selecting the latest.
    """
    with _tempdir() as b_temp_path:
        display.display("Process install dependency map")
        with _display_progress():
            dep_map = _build_dependency_map(collections, [], b_temp_path, apis, validate_certs, True, True, no_deps,
                                            allow_pre_release=allow_pre_release)

        requirements = []
        display.display("Starting collection download process to '%s'" % output_path)
        with _display_progress():
            for name, requirement in dep_map.items():
                collection_filename = "%s-%s-%s.tar.gz" % (requirement.namespace, requirement.name,
                                                           requirement.latest_version)
                dest_path = os.path.join(output_path, collection_filename)
                requirements.append({'name': collection_filename, 'version': requirement.latest_version})

                display.display("Downloading collection '%s' to '%s'" % (name, dest_path))

                if requirement.api is None and requirement.b_path and os.path.isfile(requirement.b_path):
                    shutil.copy(requirement.b_path, to_bytes(dest_path, errors='surrogate_or_strict'))
                elif requirement.api is None and requirement.b_path:
                    temp_path = to_text(b_temp_path, errors='surrogate_or_string')
                    temp_download_path = build_collection(requirement.b_path, temp_path, True)
                    shutil.move(to_bytes(temp_download_path, errors='surrogate_or_strict'),
                                to_bytes(dest_path, errors='surrogate_or_strict'))
                else:
                    b_temp_download_path = requirement.download(b_temp_path)
                    shutil.move(b_temp_download_path, to_bytes(dest_path, errors='surrogate_or_strict'))

                display.display("%s (%s) was downloaded successfully" % (name, requirement.latest_version))

            requirements_path = os.path.join(output_path, 'requirements.yml')
            display.display("Writing requirements.yml file of downloaded collections to '%s'" % requirements_path)
            with open(to_bytes(requirements_path, errors='surrogate_or_strict'), mode='wb') as req_fd:
                req_fd.write(to_bytes(yaml.safe_dump({'collections': requirements}), errors='surrogate_or_strict'))