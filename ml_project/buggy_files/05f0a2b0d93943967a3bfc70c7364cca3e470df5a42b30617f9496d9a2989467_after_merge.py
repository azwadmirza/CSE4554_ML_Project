def prep_trans_tar(opts, file_client, chunks, file_refs, pillar=None, id_=None):
    '''
    Generate the execution package from the saltenv file refs and a low state
    data structure
    '''
    gendir = tempfile.mkdtemp()
    trans_tar = salt.utils.mkstemp()
    lowfn = os.path.join(gendir, 'lowstate.json')
    pillarfn = os.path.join(gendir, 'pillar.json')
    sync_refs = [
            [salt.utils.url.create('_modules')],
            [salt.utils.url.create('_states')],
            [salt.utils.url.create('_grains')],
            [salt.utils.url.create('_renderers')],
            [salt.utils.url.create('_returners')],
            [salt.utils.url.create('_output')],
            [salt.utils.url.create('_utils')],
            ]
    with salt.utils.fopen(lowfn, 'w+') as fp_:
        fp_.write(json.dumps(chunks))
    if pillar:
        with salt.utils.fopen(pillarfn, 'w+') as fp_:
            fp_.write(json.dumps(pillar))

    if id_ is None:
        id_ = ''
    try:
        cachedir = os.path.join('salt-ssh', id_).rstrip(os.sep)
    except AttributeError:
        # Minion ID should always be a str, but don't let an int break this
        cachedir = os.path.join('salt-ssh', str(id_)).rstrip(os.sep)

    for saltenv in file_refs:
        # Location where files in this saltenv will be cached
        cache_dest_root = os.path.join(cachedir, 'files', saltenv)
        file_refs[saltenv].extend(sync_refs)
        env_root = os.path.join(gendir, saltenv)
        if not os.path.isdir(env_root):
            os.makedirs(env_root)
        for ref in file_refs[saltenv]:
            for name in ref:
                short = salt.utils.url.parse(name)[0]
                cache_dest = os.path.join(cache_dest_root, short)
                try:
                    path = file_client.cache_file(name, saltenv, cachedir=cachedir)
                except IOError:
                    path = ''
                if path:
                    tgt = os.path.join(env_root, short)
                    tgt_dir = os.path.dirname(tgt)
                    if not os.path.isdir(tgt_dir):
                        os.makedirs(tgt_dir)
                    shutil.copy(path, tgt)
                    continue
                try:
                    files = file_client.cache_dir(name, saltenv, cachedir=cachedir)
                except IOError:
                    files = ''
                if files:
                    for filename in files:
                        fn = filename[len(cache_dest):].strip('/')
                        tgt = os.path.join(
                                env_root,
                                short,
                                fn,
                                )
                        tgt_dir = os.path.dirname(tgt)
                        if not os.path.isdir(tgt_dir):
                            os.makedirs(tgt_dir)
                        shutil.copy(filename, tgt)
                    continue
    try:
        # cwd may not exist if it was removed but salt was run from it
        cwd = os.getcwd()
    except OSError:
        cwd = None
    os.chdir(gendir)
    with closing(tarfile.open(trans_tar, 'w:gz')) as tfp:
        for root, dirs, files in os.walk(gendir):
            for name in files:
                full = os.path.join(root, name)
                tfp.add(full[len(gendir):].lstrip(os.sep))
    if cwd:
        os.chdir(cwd)
    shutil.rmtree(gendir)
    return trans_tar