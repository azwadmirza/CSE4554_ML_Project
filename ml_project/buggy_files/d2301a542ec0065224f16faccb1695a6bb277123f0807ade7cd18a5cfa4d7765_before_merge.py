    def _read(self, files, envs, silent=True, key=None):
        for source_file in files:
            if source_file.endswith(self.extensions):  # pragma: no cover
                try:
                    source_data = self.file_reader(
                        io.open(
                            find_file(
                                source_file,
                                project_root=self.obj.get(
                                    'PROJECT_ROOT_FOR_DYNACONF'
                                )
                            ),
                            encoding=self.obj.get(
                                'ENCODING_FOR_DYNACONF', 'utf-8'
                            )
                        )
                    )
                    self.obj.logger.debug('{}_loader: {}'.format(
                        self.identifier, source_file))
                except IOError:
                    self.obj.logger.debug(
                        '{}_loader: {} (Ignored, file not Found)'.format(
                            self.identifier, source_file)
                    )
                    source_data = None
            else:
                # for tests it is possible to pass string
                source_data = self.string_reader(source_file)

            if not source_data:
                continue

            source_data = {
                k.lower(): value
                for k, value
                in source_data.items()
            }

            for env in envs:

                data = {}
                try:
                    data = source_data[env.lower()]
                except KeyError:
                    if env not in (self.obj.get('GLOBAL_ENV_FOR_DYNACONF'),
                                   'GLOBAL'):
                        message = '%s_loader: %s env not defined in %s' % (
                            self.identifier, env, source_file)
                        if silent:
                            self.obj.logger.warning(message)
                        else:
                            raise KeyError(message)
                    continue

                if env != self.obj.get('DEFAULT_ENV_FOR_DYNACONF'):
                    identifier = "{0}_{1}".format(self.identifier, env.lower())
                else:
                    identifier = self.identifier

                if not key:
                    self.obj.update(data, loader_identifier=identifier)
                elif key in data:
                    self.obj.set(key, data.get(key),
                                 loader_identifier=identifier)

                self.obj.logger.debug(
                    '{}_loader: {}: {}'.format(
                        self.identifier,
                        env.lower(),
                        list(data.keys()) if 'secret' in source_file else data
                    )
                )