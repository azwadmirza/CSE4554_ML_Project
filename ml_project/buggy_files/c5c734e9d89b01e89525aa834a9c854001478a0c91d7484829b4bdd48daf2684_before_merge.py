def extend_version_file(repository_root, version_file):
    """
    Extend CodeChecker version file with git information.
    """
    with open(version_file) as v_file:
        version_json_data = json.load(v_file)

    git_hash = ''
    try:
        git_hash_cmd = ['git', 'rev-parse', 'HEAD']
        git_hash = run_cmd(git_hash_cmd, repository_root)
        git_hash = git_hash.rstrip()
    except subprocess.CalledProcessError:
        LOG.exception('Failed to get last commit hash.')
    except OSError:
        LOG.exception('Failed to run command: %s', ' '.join(git_hash_cmd))
        sys.exit(1)

    version = version_json_data['version']
    version_string = str(version['major'])
    if int(version['minor']) != 0 or int(version['revision']) != 0:
        version_string += ".{0}".format(version['minor'])
    if int(version['revision']) != 0:
        version_string += ".{0}".format(version['revision'])

    git_describe = git_describe_dirty = version_string
    try:
        # The tag only (vX.Y.Z)
        git_describe_cmd = ['git', 'describe', '--always', '--tags',
                            '--abbrev=0']
        git_describe = run_cmd(git_describe_cmd, repository_root)
        git_describe = git_describe.rstrip()

        # The full dirty hash (vX.Y.Z-n-gabcdef0-tainted)
        git_describe_cmd = ['git', 'describe', '--always', '--tags',
                            '--dirty=-tainted']
        git_describe_dirty = run_cmd(git_describe_cmd, repository_root)
        git_describe_dirty = git_describe_dirty.rstrip()

        # Always replace the Git tag with the manually configured version
        # information -- but keep the "tainted" flag (if the working directory
        # differs from a commit) information visible, along with the
        # abbreviated command hash.
        # (This makes the tag compiled into the package improper, but this
        # is a design decision of the developer team!)
        git_tag = version_string
        git_tag_dirty = git_describe_dirty.replace(git_describe,
                                                   version_string)
    except subprocess.CalledProcessError:
        LOG.exception('Failed to get last commit describe.')
    except OSError:
        LOG.exception('Failed to run command: %s', ' '.join(git_describe_cmd))
        sys.exit(1)

    version_json_data['git_hash'] = git_hash
    version_json_data['git_describe'] = {'tag': git_tag,
                                         'dirty': git_tag_dirty}

    time_now = time.strftime("%Y-%m-%dT%H:%M")
    version_json_data['package_build_date'] = time_now

    # Rewrite version config file with the extended data.
    with open(version_file, 'w') as v_file:
        v_file.write(
            json.dumps(version_json_data, sort_keys=True, indent=4))

    # Show version information on the command-line.
    LOG.debug(json.dumps(version_json_data, sort_keys=True, indent=2))
    LOG.info("This is CodeChecker v%s (%s)", version_string, git_hash)

    # Show the original, Git-given describe information.
    LOG.info("Built from Git tags: %s (%s)", git_describe, git_describe_dirty)

    # Show the touched-up version information that uses the configuration file.
    LOG.info("Baked with Git tag information merged with configured version: "
             "%s (%s)", git_tag, git_tag_dirty)