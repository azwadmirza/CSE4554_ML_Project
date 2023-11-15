    def edit_config(self, candidate=None, commit=True, replace=None, diff=False, comment=None):
        """Loads the candidate configuration into the network device

        This method will load the specified candidate config into the device
        and merge with the current configuration unless replace is set to
        True.  If the device does not support config replace an errors
        is returned.

        :param candidate: The configuration to load into the device and merge
            with the current running configuration

        :param commit: Boolean value that indicates if the device candidate
            configuration should be  pushed in the running configuration or discarded.

        :param replace: If the value is True/False it indicates if running configuration should be completely
                        replace by candidate configuration. If can also take configuration file path as value,
                        the file in this case should be present on the remote host in the mentioned path as a
                        prerequisite.
        :param comment: Commit comment provided it is supported by remote host
        :return: Returns a json string with contains configuration applied on remote host, the returned
                 response on executing configuration commands and platform relevant data.
               {
                   "diff": "",
                   "response": [],
                   "request": []
               }

        """
        pass