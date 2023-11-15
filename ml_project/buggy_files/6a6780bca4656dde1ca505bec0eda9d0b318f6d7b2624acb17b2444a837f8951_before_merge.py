    def start(self):
        self._validate_parameters()

        # init with required, conditionally add optional  # TODO - drive from metadata?  Will need better
        metadata = dict(
            api_endpoint=self.api_endpoint,
            cos_endpoint=self.cos_endpoint,
            cos_bucket=self.cos_bucket)

        if self.cos_username:
            metadata['cos_username'] = self.cos_username
        if self.cos_password:
            metadata['cos_password'] = self.cos_password

        runtime = Runtime(schema_name=self.schema_name, name=self.name,
                          display_name=self.display_name, metadata=metadata)

        ex_msg = None
        resource = None
        try:
            resource = self.metadata_manager.add(self.name, runtime, replace=self.replace)
        except Exception as ex:
            ex_msg = str(ex)

        if resource:
            print("Metadata for {} runtime '{}' has been written to: {}".format(self.schema_name, self.name, resource))
        else:
            if ex_msg:
                self._log_and_exit("The following exception occurred while saving metadata '{}' for {} runtime: {}"
                                   .format(self.name, self.schema_name, ex_msg), display_help=True)
            else:
                self._log_and_exit("A failure occurred while saving metadata '{}' for {} runtime.  Check log output."
                                   .format(self.name, self.schema_name), display_help=True)