def initialize():
    """Replace original functions if the fs encoding is not utf-8."""
    if hasattr(sys, '_called_from_test'):
        return

    affected_functions = {
        certifi: ['where', 'old_where'],
        glob: ['glob'],
        io: ['open'],
        os: ['access', 'chdir', 'listdir', 'makedirs', 'mkdir', 'remove',
             'rename', 'renames', 'rmdir', 'stat', 'unlink', 'utime', 'walk'],
        os.path: ['abspath', 'basename', 'dirname', 'exists', 'getctime', 'getmtime', 'getsize',
                  'isabs', 'isdir', 'isfile', 'islink', 'join', 'normcase', 'normpath', 'realpath', 'relpath',
                  'split', 'splitext'],
        shutil: ['copyfile', 'copymode', 'move', 'rmtree'],
        tarfile: ['is_tarfile'],
        rarfile: ['is_rarfile'],
    }

    # pyOpenSSL 0.14-1 bug: it can't handle unicode input.
    # pyOpenSSL fix -> https://github.com/pyca/pyopenssl/pull/209
    # Our bug: https://github.com/pymedusa/Medusa/issues/1422
    handle_output_map = {
        certifi: _handle_output_b
    }

    if os.name != 'nt':
        affected_functions[os].extend(['chmod', 'chown', 'link', 'statvfs', 'symlink'])

    if not fs_encoding or fs_encoding.lower() not in ('utf-8', 'mbcs'):
        handle_input = _handle_input
    else:
        handle_input = None

    for k, v in viewitems(affected_functions):
        handle_output = handle_output_map.get(k, _handle_output_u)
        for f in v:
            setattr(k, f, make_closure(getattr(k, f), handle_input, handle_output))