    def _write_to_yaml(self, stream):
        """Write out the databsae to a YAML file.

        This function does not do any locking or transactions.
        """
        # map from per-spec hash code to installation record.
        installs = dict((k, v.to_dict()) for k, v in self._data.items())

        # databaes includes installation list and version.

        # NOTE: this DB version does not handle multiple installs of
        # the same spec well.  If there are 2 identical specs with
        # different paths, it can't differentiate.
        # TODO: fix this before we support multiple install locations.
        database = {
            'database' : {
                'installs' : installs,
                'version' : str(_db_version)
            }
        }

        try:
            return yaml.dump(database, stream=stream, default_flow_style=False)
        except YAMLError as e:
            raise SpackYAMLError("error writing YAML database:", str(e))