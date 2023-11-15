    def get_capabilities(self):
        """Returns the basic capabilities of the network device
        This method will provide some basic facts about the device and
        what capabilities it has to modify the configuration.  The minimum
        return from this method takes the following format.
        eg:
            {

                'rpc': [list of supported rpcs],
                'network_api': <str>,            # the name of the transport
                'device_info': {
                    'network_os': <str>,
                    'network_os_version': <str>,
                    'network_os_model': <str>,
                    'network_os_hostname': <str>,
                    'network_os_image': <str>,
                    'network_os_platform': <str>,
                },
                'device_operations': {
                    'supports_diff_replace': <bool>,       # identify if config should be merged or replaced is supported
                    'supports_commit': <bool>,             # identify if commit is supported by device or not
                    'supports_rollback': <bool>,           # identify if rollback is supported or not
                    'supports_defaults': <bool>,           # identify if fetching running config with default is supported
                    'supports_commit_comment': <bool>,     # identify if adding comment to commit is supported of not
                    'supports_onbox_diff: <bool>,          # identify if on box diff capability is supported or not
                    'supports_generate_diff: <bool>,       # identify if diff capability is supported within plugin
                    'supports_multiline_delimiter: <bool>, # identify if multiline demiliter is supported within config
                    'supports_diff_match: <bool>,          # identify if match is supported
                    'supports_diff_ignore_lines: <bool>,   # identify if ignore line in diff is supported
                    'supports_config_replace': <bool>,     # identify if running config replace with candidate config is supported
                    'supports_admin': <bool>,              # identify if admin configure mode is supported or not
                    'supports_commit_label': <bool>,       # identify if commit label is supported or not
                }
                'format': [list of supported configuration format],
                'diff_match': [list of supported match values],
                'diff_replace': [list of supported replace values],
                'output': [list of supported command output format]
            }
        :return: capability as json string
        """
        pass