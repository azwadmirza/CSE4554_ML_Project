def extend_version_file(repository_root, version_file):
    """
    Extend CodeChecker version file with build date and git information.
    """
    with open(version_file) as v_file:
        version_json_data = json.load(v_file)

    extend_with_git_information(repository_root, version_json_data)

    time_now = time.strftime("%Y-%m-%dT%H:%M")
    version_json_data['package_build_date'] = time_now

    # Rewrite version config file with the extended data.
    with open(version_file, 'w') as v_file:
        v_file.write(
            json.dumps(version_json_data, sort_keys=True, indent=4))

    # Show version information on the command-line.
    LOG.debug(json.dumps(version_json_data, sort_keys=True, indent=2))