    def get_ca_certs(self):
        # tries to find a valid CA cert in one of the
        # standard locations for the current distribution

        ca_certs = []
        paths_checked = []

        system = platform.system()
        # build a list of paths to check for .crt/.pem files
        # based on the platform type
        paths_checked.append('/etc/ssl/certs')
        if system == 'Linux':
            paths_checked.append('/etc/pki/ca-trust/extracted/pem')
            paths_checked.append('/etc/pki/tls/certs')
            paths_checked.append('/usr/share/ca-certificates/cacert.org')
        elif system == 'FreeBSD':
            paths_checked.append('/usr/local/share/certs')
        elif system == 'OpenBSD':
            paths_checked.append('/etc/ssl')
        elif system == 'NetBSD':
            ca_certs.append('/etc/openssl/certs')
        elif system == 'SunOS':
            paths_checked.append('/opt/local/etc/openssl/certs')

        # fall back to a user-deployed cert in a standard
        # location if the OS platform one is not available
        paths_checked.append('/etc/ansible')

        tmp_fd, tmp_path = tempfile.mkstemp()
        to_add_fd, to_add_path = tempfile.mkstemp()
        to_add = False

        # Write the dummy ca cert if we are running on Mac OS X
        if system == 'Darwin':
            os.write(tmp_fd, b_DUMMY_CA_CERT)
            # Default Homebrew path for OpenSSL certs
            paths_checked.append('/usr/local/etc/openssl')

        # for all of the paths, find any  .crt or .pem files
        # and compile them into single temp file for use
        # in the ssl check to speed up the test
        for path in paths_checked:
            if os.path.exists(path) and os.path.isdir(path):
                dir_contents = os.listdir(path)
                for f in dir_contents:
                    full_path = os.path.join(path, f)
                    if os.path.isfile(full_path) and os.path.splitext(f)[1] in ('.crt','.pem'):
                        try:
                            cert_file = open(full_path, 'rb')
                            cert = cert_file.read()
                            cert_file.close()
                            os.write(tmp_fd, cert)
                            os.write(tmp_fd, b('\n'))
                            if full_path not in LOADED_VERIFY_LOCATIONS:
                                to_add = True
                                os.write(to_add_fd, cert)
                                os.write(to_add_fd, b('\n'))
                                LOADED_VERIFY_LOCATIONS.add(full_path)
                        except (OSError, IOError):
                            pass

        if not to_add:
            to_add_path = None
        return (tmp_path, to_add_path, paths_checked)