def get_semver(tag):
    '''Return 'Semantic Version' from tag string'''
    try:
        version = str(semantic_version.Version.coerce(tag, partial=True))
            # tuple of major, minor, build, pre-release, patch
            # 5.6b2 --> 5.6-b2
    except ValueError:
        print('''*** Failed to parse Semantic Version from git tag '{0}'.
        Expecting tag name like '5.7b2', 'leo-4.9.12', 'v4.3' for releases.
        This version can't be uploaded to PyPi.org.'''.format(tag))
        version = tag
    return version