    def start(self):
        include_invalid = not self.valid_only
        runtimes = self.metadata_manager.get_all_metadata_summary(include_invalid=include_invalid)

        if not runtimes:
            print("No metadata available for external runtimes at : '{}'"
                  .format(self.metadata_manager.get_metadata_location))
            return

        if self.json_output:
            [print('Runtime: {} {}\n{}'.
                   format(rt.name, "**INVALID**" if rt.reason and len(rt.reason) > 0 else "", rt.to_json()))
             for rt in runtimes]
        else:
            sorted_runtimes = sorted(runtimes, key=lambda runtime: runtime.name)
            # pad to width of longest runtime name
            max_name_len = 0
            max_resource_len = 0
            for runtime in sorted_runtimes:
                max_name_len = max(len(runtime.name), max_name_len)
                max_resource_len = max(len(runtime.resource), max_resource_len)

            print("Available metadata for external runtimes:")
            for runtime in sorted_runtimes:
                invalid = ""
                if runtime.reason and len(runtime.reason) > 0:
                    invalid = "**INVALID** ({})".format(runtime.reason)
                print("  %s  %s  %s" % (runtime.name.ljust(max_name_len),
                                        runtime.resource.ljust(max_resource_len),
                                        invalid))