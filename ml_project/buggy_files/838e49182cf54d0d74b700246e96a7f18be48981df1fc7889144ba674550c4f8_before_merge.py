    def create_pipfile(self, python=None):
        """Creates the Pipfile, filled with juicy defaults."""
        config_parser = ConfigOptionParser(name=self.name)
        install = dict(config_parser.get_config_section('install'))
        indexes = install.get('extra-index-url', '').lstrip('\n').split('\n')

        if PIPENV_TEST_INDEX:
            sources = [{u'url': PIPENV_TEST_INDEX, u'verify_ssl': True, u'name': u'custom'}]
        else:
            # Default source.
            pypi_source = {u'url': u'https://pypi.python.org/simple', u'verify_ssl': True, u'name': 'pypi'}
            sources = [pypi_source]

            for i, index in enumerate(indexes):
                if not index:
                    continue
                source_name = 'pip_index_{}'.format(i)
                verify_ssl = index.startswith('https')

                sources.append({u'url': index, u'verify_ssl': verify_ssl, u'name': source_name})

        data = {
            u'source': sources,

            # Default packages.
            u'packages': {},
            u'dev-packages': {},

        }

        # Default requires.
        data[u'requires'] = {'python_version': python_version(self.which('python'))[:len('2.7')]}

        self.write_toml(data, 'Pipfile')