    def post_run(self, workspace):
        if self.save_cpa_properties.value:
            self.write_properties_file(workspace)
        if self.create_workspace_file.value:
            self.write_workspace_file(workspace)
        if self.db_type == DB_MYSQL_CSV:
            path = self.directory.get_absolute_path(
                None if workspace is None else workspace.measurements
            )
            if not os.path.isdir(path):
                os.makedirs(path)
            self.write_mysql_table_defs(workspace)
            self.write_csv_data(workspace)
        else:
            self.write_post_run_measurements(workspace)