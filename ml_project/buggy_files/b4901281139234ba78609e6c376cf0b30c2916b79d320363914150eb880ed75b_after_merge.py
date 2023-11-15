def pip_install(package_name=None, r=None, allow_global=False):
    # Prevent invalid shebangs with Homebrew-installed Python: https://bugs.python.org/issue22490
    os.environ.pop('__PYVENV_LAUNCHER__', None)
    if r:
        c = delegator.run('{0} install -r {1} --require-hashes -i {2}'.format(which_pip(allow_global=allow_global), r, project.source['url']))
    else:
        c = delegator.run('{0} install "{1}" -i {2}'.format(which_pip(allow_global=allow_global), package_name, project.source['url']))
    return c