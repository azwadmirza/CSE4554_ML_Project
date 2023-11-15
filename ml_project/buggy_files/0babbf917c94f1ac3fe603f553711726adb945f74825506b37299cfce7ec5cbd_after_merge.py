def build():
    """Build the application"""
    logger.info('Deleting directories build and dist')
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('dist', ignore_errors=True)
    shutil.rmtree('BleachBit-Portable', ignore_errors=True)

    logger.info('Running py2exe')
    shutil.copyfile('bleachbit.py', 'bleachbit_console.py')
    cmd = sys.executable + ' -OO setup.py py2exe'
    run_cmd(cmd)
    assert_exist('dist\\bleachbit.exe')
    assert_exist('dist\\bleachbit_console.exe')
    os.remove('bleachbit_console.py')

    if not os.path.exists('dist'):
        os.makedirs('dist')

    logger.info('Copying GTK files and icon')
    copytree(GTK_DIR + '\\etc', 'dist\\etc')
    copytree(GTK_DIR + '\\lib', 'dist\\lib')
    for subpath in ['fontconfig', 'fonts', 'icons', 'themes']:
        copytree(os.path.join(GTK_DIR, 'share', subpath), 'dist\\share\\' + subpath)
    SCHEMAS_DIR = 'share\\glib-2.0\\schemas'
    os.makedirs(os.path.join('dist', SCHEMAS_DIR))
    shutil.copyfile(os.path.join(GTK_DIR, SCHEMAS_DIR, 'gschemas.compiled'), os.path.join('dist', SCHEMAS_DIR, 'gschemas.compiled'))
    shutil.copyfile('bleachbit.png',  'dist\\share\\bleachbit.png')
    for dll in glob.glob1(GTK_DIR, '*.dll'):
        shutil.copyfile(os.path.join(GTK_DIR,dll), 'dist\\'+dll)

    os.mkdir('dist\\data')
    shutil.copyfile('data\\app-menu.ui', 'dist\\data\\app-menu.ui')

    logger.info('Copying CA bundle')
    import requests
    shutil.copyfile(requests.utils.DEFAULT_CA_BUNDLE_PATH, os.path.join('dist', 'cacert.pem'))

    logger.info('Copying BleachBit localizations')
    shutil.rmtree('dist\\share\\locale', ignore_errors=True)
    copytree('locale', 'dist\\share\\locale')
    assert_exist('dist\\share\\locale\\es\\LC_MESSAGES\\bleachbit.mo')

    logger.info('Copying BleachBit cleaners')
    if not os.path.exists('dist\\share\\cleaners'):
        os.makedirs('dist\\share\\cleaners')
    cleaners_files = recursive_glob('cleaners', ['*.xml'])
    for file in cleaners_files:
        shutil.copy(file,  'dist\\share\\cleaners')

    logger.info('Checking for CleanerML')
    assert_exist('dist\\share\\cleaners\\internet_explorer.xml')

    logger.info('Copying license')
    shutil.copy('COPYING', 'dist')

    sign_code('dist\\bleachbit.exe')
    sign_code('dist\\bleachbit_console.exe')

    assert_execute_console()