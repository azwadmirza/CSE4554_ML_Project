    def run_as_data_tool(self, workspace):
        """Run the module as a data tool

        ExportToDatabase has two modes - writing CSVs and writing directly.
        We write CSVs in post_run. We write directly in run.
        """
        #
        # The measurements may have been created by an old copy of CP. We
        # have to hack our measurement column cache to circumvent this.
        #
        m = workspace.measurements
        assert isinstance(m, cellprofiler_core.measurement.Measurements)
        d = self.get_dictionary()
        columns = m.get_measurement_columns()
        for i, (object_name, feature_name, coltype) in enumerate(columns):
            if (
                object_name == cellprofiler_core.measurement.IMAGE
                and feature_name.startswith(C_THUMBNAIL)
            ):
                columns[i] = (
                    object_name,
                    feature_name,
                    cellprofiler_core.measurement.COLTYPE_LONGBLOB,
                )
        columns = self.filter_measurement_columns(columns)
        d[D_MEASUREMENT_COLUMNS] = columns

        if not self.prepare_run(workspace, as_data_tool=True):
            return
        self.prepare_group(workspace, None, None)
        if self.db_type != DB_MYSQL_CSV:
            workspace.measurements.is_first_image = True

            for i in range(workspace.measurements.image_set_count):
                if i > 0:
                    workspace.measurements.next_image_set()
                self.run(workspace)
        else:
            workspace.measurements.image_set_number = (
                workspace.measurements.image_set_count
            )
        self.post_run(workspace)