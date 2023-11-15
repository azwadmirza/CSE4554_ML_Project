def git_version(file, version=None):
    '''Fetch from Git: {tag} {distance-from-tag} {current commit hash}
       Return as semantic version string compliant with PEP440'''
    root = os.path.dirname(os.path.realpath(file))
    try:
        tag, distance, commit = g.gitDescribe(root)
            # 5.6b2, 55, e1129da
        ctag = clean_git_tag(tag)
        #version = get_semver(ctag)
        version = ctag
        if int(distance) > 0:
            version = '{}-dev{}'.format(version, distance)
    except IndexError:
        print('Attempt to `git describe` failed with IndexError')
    except FileNotFoundError:
        print('Attempt to `git describe` failed with FileNotFoundError')
    return version