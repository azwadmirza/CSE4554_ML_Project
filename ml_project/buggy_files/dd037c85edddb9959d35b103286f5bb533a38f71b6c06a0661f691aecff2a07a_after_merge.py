    def load_data(self, policy_data, file_uri, validate=None,
                  session_factory=None, config=None):
        self.structure.validate(policy_data)

        # Use passed in policy exec configuration or default on loader
        config = config or self.policy_config

        # track policy resource types and only load if needed.
        rtypes = set(self.structure.get_resource_types(policy_data))

        missing = load_resources(list(rtypes))
        if missing:
            self._handle_missing_resources(policy_data, missing)

        if schema and (validate is not False or (
                validate is None and
                self.default_schema_validate)):
            errors = self.validator.validate(policy_data, tuple(rtypes))
            if errors:
                raise PolicyValidationError(
                    "Failed to validate policy %s\n %s\n" % (
                        errors[1], errors[0]))

        collection = self.collection_class.from_data(
            policy_data, config, session_factory)

        # non schema validation of policies isnt optional its
        # become a lazy initialization point for resources.
        #
        # it would be good to review where we do validation
        # as we also have to do after provider policy
        # initialization due to the region expansion.
        #
        # ie we should defer this to callers
        # [p.validate() for p in collection]
        return collection