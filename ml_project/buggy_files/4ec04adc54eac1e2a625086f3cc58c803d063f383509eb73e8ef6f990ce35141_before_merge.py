    def finalize_options(self):
        Sdist.finalize_options(self)
        if 'SKIP_BOOTSTRAP_DOWNLOAD' in os.environ:
            log('Please stop using \'SKIP_BOOTSTRAP_DOWNLOAD\' and use '
                '\'DOWNLOAD_BOOTSTRAP_SCRIPT\' instead')

        if 'DOWNLOAD_BOOTSTRAP_SCRIPT' in os.environ:
            download_bootstrap_script = os.environ.get(
                'DOWNLOAD_BOOTSTRAP_SCRIPT', '0'
            )
            self.download_bootstrap_script = download_bootstrap_script == '1'