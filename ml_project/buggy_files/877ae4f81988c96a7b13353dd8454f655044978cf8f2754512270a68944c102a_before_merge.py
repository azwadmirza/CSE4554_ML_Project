    def setup(self):
        if not self.setup_done:
            if not self._options.get('namespace', None):
                msg = 'Set a namespace with --oio-ns, OIO_NS\n'
                raise exceptions.CommandError('Missing parameter: \n%s' % msg)
            self.namespace = self._options['namespace']
            sds_conf = load_namespace_conf(self.namespace) or {}
            if not self._options.get('proxyd_url') and 'proxy' in sds_conf:
                proxyd_url = 'http://%s' % sds_conf.get('proxy')
                self._options['proxyd_url'] = proxyd_url
            validate_options(self._options)
            LOG.debug('Using parameters %s' % self._options)
            self.setup_done = True
            self._admin_mode = self._options.get('admin_mode')
            if 'meta1_digits' in sds_conf:
                self._meta1_digits = int(sds_conf["meta1_digits"])