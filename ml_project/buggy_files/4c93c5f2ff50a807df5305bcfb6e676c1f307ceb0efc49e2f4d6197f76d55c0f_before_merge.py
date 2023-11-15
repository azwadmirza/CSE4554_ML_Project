def _debug_tarball_suffix():
    now = datetime.now()
    suffix = now.strftime('%Y-%m-%d-%H%M%S')

    git = which('git')
    if not git:
        return 'nobranch-nogit-%s' % suffix

    with working_dir(spack.spack_root):
        if not os.path.isdir('.git'):
            return 'nobranch.nogit.%s' % suffix

        symbolic = git(
            'rev-parse', '--abbrev-ref', '--short', 'HEAD', output=str).strip()
        commit = git(
            'rev-parse', '--short', 'HEAD', output=str).strip()

        if symbolic == commit:
            return "nobranch.%s.%s" % (commit, suffix)
        else:
            return "%s.%s.%s" % (symbolic, commit, suffix)