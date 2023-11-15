def git_version(file):
    '''Fetch from Git: {tag} {distance-from-tag} {current commit hash}
       Return as semantic version string compliant with PEP440'''
    root = os.path.dirname(os.path.realpath(file))
    tag, distance, commit = g.gitDescribe(root)
        # 5.6b2, 55, e1129da
    ctag = clean_git_tag(tag)
    try:
        version = semantic_version.Version.coerce(ctag, partial=True)
            # tuple of major, minor, build, pre-release, patch
            # 5.6b2 --> 5.6-b2
    except ValueError:
        print('''*** Failed to parse Semantic Version from git tag '{0}'.
        Expecting tag name like '5.7b2', 'leo-4.9.12', 'v4.3' for releases.
        This version can't be uploaded to PyPi.org.'''.format(tag))
        version = tag
    if int(distance) > 0:
        version = '{}-dev{}'.format(version, distance)
    return version