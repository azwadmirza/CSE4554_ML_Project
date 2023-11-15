def delete_unnecessary():
    logger.info('Deleting unnecessary files')
    # Remove SVG to reduce space and avoid this error
    # Error loading theme icon 'dialog-warning' for stock: Unable to load image-loading module: C:/Python27/Lib/site-packages/gtk-2.0/runtime/lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.dll: `C:/Python27/Lib/site-packages/gtk-2.0/runtime/lib/gdk-pixbuf-2.0/2.10.0/loaders/libpixbufloader-svg.dll': The specified module could not be found.
    # https://bugs.launchpad.net/bleachbit/+bug/1650907
    delete_paths = [
        r'_win32sysloader.pyd',
        r'lib\gdk-pixbuf-2.0',
        r'lib\gdbus-2.0',
        r'perfmon.pyd',
        r'select.pyd',
        r'servicemanager.pyd',
        r'share\themes\default',
        r'share\themes\emacs',
        r'share\fontconfig',
        r'share\glib-2.0',
        r'share\icons\highcontrast',
        r'share\themes',
        r'win32evtlog.pyd',
        r'win32pipe.pyd',
        r'win32wnet.pyd',
    ]
    for path in delete_paths:
        path = r'dist\{}'.format(path)
        if not os.path.exists(path):
            logger.warning('Path does not exist: ' + path)
            continue
        if os.path.isdir(path):
            this_dir_size = get_dir_size(path)
            shutil.rmtree(path, ignore_errors=True)
            logger.info('Deleting directory {} saved {:,} B'.format(
                path, this_dir_size))
        else:
            logger.info('Deleting file {} saved {:,} B'.format(
                path, os.path.getsize(path)))
            os.remove(path)
    # by wildcard with recursive search
    delete_wildcards = [
        '*.a',
        '*.def',
        '*.lib',
        'atk10.mo',
        'gdk-pixbuf.mo',
        'gettext-runtime.mo',
        'glib20.mo',
        'gtk20-properties.mo',
        'libgsf.mo',
    ]
    for wc in delete_wildcards:
        total_size = 0
        for f in recursive_glob('dist', [wc]):
            total_size += os.path.getsize(f)
            os.remove(f)
        logger.info('Deleting wildcard {} saved {:,}B'.format(wc, total_size))