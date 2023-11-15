    def __link_file_check(self):
        """ outputs_to_working_directory breaks library uploads where data is
        linked.  This method is a hack that solves that problem, but is
        specific to the upload tool and relies on an injected job param.  This
        method should be removed ASAP and replaced with some properly generic
        and stateful way of determining link-only datasets. -nate
        """
        if self.tool:
            job = self.get_job()
            param_dict = job.get_param_values(self.app)
            return self.tool.id == 'upload1' and param_dict.get('link_data_only', None) == 'link_to_files'
        else:
            # The tool is unavailable, we try to move the outputs.
            return False