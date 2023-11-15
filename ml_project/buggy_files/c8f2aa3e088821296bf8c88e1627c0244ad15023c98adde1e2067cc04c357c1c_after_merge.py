    def post_run(self, workspace):
        if self.save_cpa_properties.value:
            self.write_properties_file(workspace)
        if self.create_workspace_file.value:
            self.write_workspace_file(workspace)
        self.write_post_run_measurements(workspace)