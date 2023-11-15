def write_xattr(path, key, value):
    # This mess below finds the best xattr tool for the job
    try:
        # try the pyxattr module...
        import xattr

        if hasattr(xattr, 'set'):  # pyxattr
            # Unicode arguments are not supported in python-pyxattr until
            # version 0.5.0
            # See https://github.com/rg3/youtube-dl/issues/5498
            pyxattr_required_version = '0.5.0'
            if version_tuple(xattr.__version__) < version_tuple(pyxattr_required_version):
                # TODO: fallback to CLI tools
                raise XAttrUnavailableError(
                    'python-pyxattr is detected but is too old. '
                    'youtube-dl requires %s or above while your version is %s. '
                    'Falling back to other xattr implementations' % (
                        pyxattr_required_version, xattr.__version__))

            setxattr = xattr.set
        else:  # xattr
            setxattr = xattr.setxattr

        try:
            setxattr(path, key, value)
        except EnvironmentError as e:
            raise XAttrMetadataError(e.errno, e.strerror)

    except ImportError:
        if compat_os_name == 'nt':
            # Write xattrs to NTFS Alternate Data Streams:
            # http://en.wikipedia.org/wiki/NTFS#Alternate_data_streams_.28ADS.29
            assert ':' not in key
            assert os.path.exists(path)

            ads_fn = path + ':' + key
            try:
                with open(ads_fn, 'wb') as f:
                    f.write(value)
            except EnvironmentError as e:
                raise XAttrMetadataError(e.errno, e.strerror)
        else:
            user_has_setfattr = check_executable('setfattr', ['--version'])
            user_has_xattr = check_executable('xattr', ['-h'])

            if user_has_setfattr or user_has_xattr:

                value = value.decode('utf-8')
                if user_has_setfattr:
                    executable = 'setfattr'
                    opts = ['-n', key, '-v', value]
                elif user_has_xattr:
                    executable = 'xattr'
                    opts = ['-w', key, value]

                cmd = ([encodeFilename(executable, True)] +
                       [encodeArgument(o) for o in opts] +
                       [encodeFilename(path, True)])

                try:
                    p = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                except EnvironmentError as e:
                    raise XAttrMetadataError(e.errno, e.strerror)
                stdout, stderr = p.communicate()
                stderr = stderr.decode('utf-8', 'replace')
                if p.returncode != 0:
                    raise XAttrMetadataError(p.returncode, stderr)

            else:
                # On Unix, and can't find pyxattr, setfattr, or xattr.
                if sys.platform.startswith('linux'):
                    raise XAttrUnavailableError(
                        "Couldn't find a tool to set the xattrs. "
                        "Install either the python 'pyxattr' or 'xattr' "
                        "modules, or the GNU 'attr' package "
                        "(which contains the 'setfattr' tool).")
                else:
                    raise XAttrUnavailableError(
                        "Couldn't find a tool to set the xattrs. "
                        "Install either the python 'xattr' module, "
                        "or the 'xattr' binary.")