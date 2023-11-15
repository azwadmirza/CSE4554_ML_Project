def _data_path(path=None, force_update=False, update_path=True, download=True,
               name=None, check_version=False, return_version=False,
               archive_name=None):
    """Aux function."""
    key = {
        'fake': 'MNE_DATASETS_FAKE_PATH',
        'misc': 'MNE_DATASETS_MISC_PATH',
        'sample': 'MNE_DATASETS_SAMPLE_PATH',
        'spm': 'MNE_DATASETS_SPM_FACE_PATH',
        'somato': 'MNE_DATASETS_SOMATO_PATH',
        'brainstorm': 'MNE_DATASETS_BRAINSTORM_PATH',
        'testing': 'MNE_DATASETS_TESTING_PATH',
        'multimodal': 'MNE_DATASETS_MULTIMODAL_PATH',
        'fnirs_motor': 'MNE_DATASETS_FNIRS_MOTOR_PATH',
        'opm': 'MNE_DATASETS_OPM_PATH',
        'visual_92_categories': 'MNE_DATASETS_VISUAL_92_CATEGORIES_PATH',
        'kiloword': 'MNE_DATASETS_KILOWORD_PATH',
        'mtrf': 'MNE_DATASETS_MTRF_PATH',
        'fieldtrip_cmc': 'MNE_DATASETS_FIELDTRIP_CMC_PATH',
        'phantom_4dbti': 'MNE_DATASETS_PHANTOM_4DBTI_PATH',
        'limo': 'MNE_DATASETS_LIMO_PATH',
        'refmeg_noise': 'MNE_DATASETS_REFMEG_NOISE_PATH',
    }[name]

    path = _get_path(path, key, name)
    # To update the testing or misc dataset, push commits, then make a new
    # release on GitHub. Then update the "releases" variable:
    releases = dict(testing='0.106', misc='0.6')
    # And also update the "md5_hashes['testing']" variable below.
    # To update any other dataset, update the data archive itself (upload
    # an updated version) and update the md5 hash.

    # try to match url->archive_name->folder_name
    urls = dict(  # the URLs to use
        brainstorm=dict(
            bst_auditory='https://osf.io/5t9n8/download?version=1',
            bst_phantom_ctf='https://osf.io/sxr8y/download?version=1',
            bst_phantom_elekta='https://osf.io/dpcku/download?version=1',
            bst_raw='https://osf.io/9675n/download?version=2',
            bst_resting='https://osf.io/m7bd3/download?version=3'),
        fake='https://github.com/mne-tools/mne-testing-data/raw/master/'
             'datasets/foo.tgz',
        misc='https://codeload.github.com/mne-tools/mne-misc-data/'
             'tar.gz/%s' % releases['misc'],
        sample='https://osf.io/86qa2/download?version=5',
        somato='https://osf.io/tp4sg/download?version=7',
        spm='https://osf.io/je4s8/download?version=2',
        testing='https://codeload.github.com/mne-tools/mne-testing-data/'
                'tar.gz/%s' % releases['testing'],
        multimodal='https://ndownloader.figshare.com/files/5999598',
        fnirs_motor='https://osf.io/dj3eh/download?version=1',
        opm='https://osf.io/p6ae7/download?version=2',
        visual_92_categories=[
            'https://osf.io/8ejrs/download?version=1',
            'https://osf.io/t4yjp/download?version=1'],
        mtrf='https://osf.io/h85s2/download?version=1',
        kiloword='https://osf.io/qkvf9/download?version=1',
        fieldtrip_cmc='https://osf.io/j9b6s/download?version=1',
        phantom_4dbti='https://osf.io/v2brw/download?version=2',
        refmeg_noise='https://osf.io/drt6v/download?version=1',
    )
    # filename of the resulting downloaded archive (only needed if the URL
    # name does not match resulting filename)
    archive_names = dict(
        fieldtrip_cmc='SubjectCMC.zip',
        kiloword='MNE-kiloword-data.tar.gz',
        misc='mne-misc-data-%s.tar.gz' % releases['misc'],
        mtrf='mTRF_1.5.zip',
        multimodal='MNE-multimodal-data.tar.gz',
        fnirs_motor='MNE-fNIRS-motor-data.tgz',
        opm='MNE-OPM-data.tar.gz',
        sample='MNE-sample-data-processed.tar.gz',
        somato='MNE-somato-data.tar.gz',
        spm='MNE-spm-face.tar.gz',
        testing='mne-testing-data-%s.tar.gz' % releases['testing'],
        visual_92_categories=['MNE-visual_92_categories-data-part1.tar.gz',
                              'MNE-visual_92_categories-data-part2.tar.gz'],
        phantom_4dbti='MNE-phantom-4DBTi.zip',
        refmeg_noise='sample_reference_MEG_noise-raw.zip'
    )
    # original folder names that get extracted (only needed if the
    # archive does not extract the right folder name; e.g., usually GitHub)
    folder_origs = dict(  # not listed means None (no need to move)
        misc='mne-misc-data-%s' % releases['misc'],
        testing='mne-testing-data-%s' % releases['testing'],
    )
    # finally, where we want them to extract to (only needed if the folder name
    # is not the same as the last bit of the archive name without the file
    # extension)
    folder_names = dict(
        brainstorm='MNE-brainstorm-data',
        fake='foo',
        misc='MNE-misc-data',
        mtrf='mTRF_1.5',
        sample='MNE-sample-data',
        testing='MNE-testing-data',
        visual_92_categories='MNE-visual_92_categories-data',
        fieldtrip_cmc='MNE-fieldtrip_cmc-data',
        phantom_4dbti='MNE-phantom-4DBTi',
        refmeg_noise='MNE-refmeg-noise-data'
    )
    md5_hashes = dict(
        brainstorm=dict(
            bst_auditory='fa371a889a5688258896bfa29dd1700b',
            bst_phantom_ctf='80819cb7f5b92d1a5289db3fb6acb33c',
            bst_phantom_elekta='1badccbe17998d18cc373526e86a7aaf',
            bst_raw='fa2efaaec3f3d462b319bc24898f440c',
            bst_resting='70fc7bf9c3b97c4f2eab6260ee4a0430'),
        fake='3194e9f7b46039bb050a74f3e1ae9908',
        misc='e00808c3b05123059e2cf49ff276e919',
        sample='12b75d1cb7df9dfb4ad73ed82f61094f',
        somato='32fd2f6c8c7eb0784a1de6435273c48b',
        spm='9f43f67150e3b694b523a21eb929ea75',
        testing='d67eff9e1089f15b69f88931dbbf35df',
        multimodal='26ec847ae9ab80f58f204d09e2c08367',
        fnirs_motor='c4935d19ddab35422a69f3326a01fef8',
        opm='370ad1dcfd5c47e029e692c85358a374',
        visual_92_categories=['74f50bbeb65740903eadc229c9fa759f',
                              '203410a98afc9df9ae8ba9f933370e20'],
        kiloword='3a124170795abbd2e48aae8727e719a8',
        mtrf='273a390ebbc48da2c3184b01a82e4636',
        fieldtrip_cmc='6f9fd6520f9a66e20994423808d2528c',
        phantom_4dbti='938a601440f3ffa780d20a17bae039ff',
        refmeg_noise='779fecd890d98b73a4832e717d7c7c45'
    )
    assert set(md5_hashes.keys()) == set(urls.keys())
    url = urls[name]
    hash_ = md5_hashes[name]
    folder_orig = folder_origs.get(name, None)
    if name == 'brainstorm':
        assert archive_name is not None
        url = [url[archive_name.split('.')[0]]]
        folder_path = [op.join(path, folder_names[name],
                               archive_name.split('.')[0])]
        hash_ = [hash_[archive_name.split('.')[0]]]
        archive_name = [archive_name]
    else:
        url = [url] if not isinstance(url, list) else url
        hash_ = [hash_] if not isinstance(hash_, list) else hash_
        archive_name = archive_names.get(name)
        if archive_name is None:
            archive_name = [u.split('/')[-1] for u in url]
        if not isinstance(archive_name, list):
            archive_name = [archive_name]
        folder_path = [op.join(path, folder_names.get(name, a.split('.')[0]))
                       for a in archive_name]
    if not isinstance(folder_orig, list):
        folder_orig = [folder_orig] * len(url)
    folder_path = [op.abspath(f) for f in folder_path]
    assert hash_ is not None
    assert all(isinstance(x, list) for x in (url, archive_name, hash_,
                                             folder_path))
    assert len(url) == len(archive_name) == len(hash_) == len(folder_path)
    logger.debug('URL:          %s' % (url,))
    logger.debug('archive_name: %s' % (archive_name,))
    logger.debug('hash:         %s' % (hash_,))
    logger.debug('folder_path:  %s' % (folder_path,))

    need_download = any(not op.exists(f) for f in folder_path)
    if need_download and not download:
        return ''

    if need_download or force_update:
        logger.debug('Downloading: need_download=%s, force_update=%s'
                     % (need_download, force_update))
        for f in folder_path:
            logger.debug('  Exists: %s: %s' % (f, op.exists(f)))
        if name == 'brainstorm':
            if '--accept-brainstorm-license' in sys.argv:
                answer = 'y'
            else:
                answer = input('%sAgree (y/[n])? ' % _bst_license_text)
            if answer.lower() != 'y':
                raise RuntimeError('You must agree to the license to use this '
                                   'dataset')
        assert len(url) == len(hash_)
        assert len(url) == len(archive_name)
        assert len(url) == len(folder_orig)
        assert len(url) == len(folder_path)
        assert len(url) > 0
        # 1. Get all the archives
        full_name = list()
        for u, an, h, fo in zip(url, archive_name, hash_, folder_orig):
            remove_archive, full = _download(path, u, an, h)
            full_name.append(full)
        del archive_name
        # 2. Extract all of the files
        remove_dir = True
        for u, fp, an, h, fo in zip(url, folder_path, full_name, hash_,
                                    folder_orig):
            _extract(path, name, fp, an, fo, remove_dir)
            remove_dir = False  # only do on first iteration
        # 3. Remove all of the archives
        if remove_archive:
            for an in full_name:
                os.remove(op.join(path, an))

        logger.info('Successfully extracted to: %s' % folder_path)

    _do_path_update(path, update_path, key, name)
    path = folder_path[0]

    # compare the version of the dataset and mne
    data_version = _dataset_version(path, name)
    # 0.7 < 0.7.git should be False, therefore strip
    if check_version and (LooseVersion(data_version) <
                          LooseVersion(mne_version.strip('.git'))):
        warn('The {name} dataset (version {current}) is older than '
             'mne-python (version {newest}). If the examples fail, '
             'you may need to update the {name} dataset by using '
             'mne.datasets.{name}.data_path(force_update=True)'.format(
                 name=name, current=data_version, newest=mne_version))
    return (path, data_version) if return_version else path