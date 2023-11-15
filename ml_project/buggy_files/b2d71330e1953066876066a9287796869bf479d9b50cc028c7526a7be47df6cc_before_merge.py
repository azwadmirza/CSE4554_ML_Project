def pip(args):
    # First things first, get a recent (stable) version of pip.
    if not os.path.exists(TOX_PIP_DIR):
        subprocess.check_call([sys.executable, '-m', 'pip',
                               '--disable-pip-version-check',
                               'install', '-t', TOX_PIP_DIR,
                               'pip'])
        shutil.rmtree(glob(os.path.join(TOX_PIP_DIR, 'pip-*.dist-info'))[0])
    # And use that version.
    for n, a in enumerate(args):
        if not a.startswith('-'):
            if a in 'install' and '-e' in args[n:]:
                args.insert(n + 1, '--no-use-pep517')
            break
    subprocess.check_call([sys.executable, os.path.join(TOX_PIP_DIR, 'pip')] + args)