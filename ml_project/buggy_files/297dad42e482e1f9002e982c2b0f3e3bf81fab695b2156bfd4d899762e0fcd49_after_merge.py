    def write_mysql_table_per_well(self, pipeline, image_set_list, fid=None):
        """Write SQL statements to generate a per-well table

        pipeline - the pipeline being run (to get feature names)
        image_set_list -
        fid - file handle of file to write or None if statements
              should be written to a separate file.
        """
        if fid is None:
            file_name = "SQL__Per_Well_SETUP.SQL"
            path_name = self.make_full_filename(file_name)
            fid = open(path_name, "wt")
            needs_close = True
        else:
            needs_close = False
        fid.write("USE %s;\n" % self.db_name.value)
        table_prefix = self.get_table_prefix()
        #
        # Do in two passes. Pass # 1 makes the column name mappings for the
        # well table. Pass # 2 writes the SQL
        #
        mappings = self.get_column_name_mappings(pipeline, image_set_list)
        object_names = self.get_object_names(pipeline, image_set_list)
        columns = self.get_pipeline_measurement_columns(pipeline, image_set_list)
        for aggname in self.agg_well_names:
            well_mappings = ColumnNameMapping()
            for do_mapping, do_write in ((True, False), (False, True)):
                if do_write:
                    fid.write(
                        "CREATE TABLE %sPer_Well_%s AS SELECT "
                        % (self.get_table_prefix(), aggname)
                    )
                for i, object_name in enumerate(
                    object_names + [cellprofiler_core.measurement.IMAGE]
                ):
                    if object_name == cellprofiler_core.measurement.IMAGE:
                        object_table_name = "IT"
                    elif self.separate_object_tables == OT_COMBINE:
                        object_table_name = "OT"
                    else:
                        object_table_name = "OT%d" % (i + 1)
                    for column in columns:
                        column_object_name, feature, data_type = column[:3]
                        if column_object_name != object_name:
                            continue
                        if self.ignore_feature(object_name, feature):
                            continue
                        #
                        # Don't take an aggregate on a string column
                        #
                        if data_type.startswith(
                            cellprofiler_core.measurement.COLTYPE_VARCHAR
                        ):
                            continue
                        feature_name = "%s_%s" % (object_name, feature)
                        colname = mappings[feature_name]
                        well_colname = "%s_%s" % (aggname, colname)
                        if do_mapping:
                            well_mappings.add(well_colname)
                        if do_write:
                            fid.write(
                                "%s(%s.%s) as %s,\n"
                                % (
                                    aggname,
                                    object_table_name,
                                    colname,
                                    well_mappings[well_colname],
                                )
                            )
            fid.write(
                "IT.Image_Metadata_Plate, IT.Image_Metadata_Well "
                "FROM %sPer_Image IT\n" % table_prefix
            )
            if len(object_names) == 0:
                pass
            elif self.separate_object_tables == OT_COMBINE:
                fid.write(
                    "JOIN %s OT ON IT.%s = OT.%s\n"
                    % (
                        self.get_table_name(cellprofiler_core.measurement.OBJECT),
                        C_IMAGE_NUMBER,
                        C_IMAGE_NUMBER,
                    )
                )
            elif len(object_names) == 1:
                fid.write(
                    "JOIN %s OT1 ON IT.%s = OT1.%s\n"
                    % (
                        self.get_table_name(object_names[0]),
                        C_IMAGE_NUMBER,
                        C_IMAGE_NUMBER,
                    )
                )
            else:
                #
                # We make up a table here that lists all of the possible
                # image and object numbers from any of the object numbers.
                # We need this to do something other than a cartesian join
                # between object tables.
                #
                fid.write(
                    "RIGHT JOIN (SELECT DISTINCT %s, %s FROM\n"
                    % (C_IMAGE_NUMBER, C_OBJECT_NUMBER)
                )
                fid.write(
                    "(SELECT %s, %s_%s as %s FROM %s\n"
                    % (
                        C_IMAGE_NUMBER,
                        object_names[0],
                        M_NUMBER_OBJECT_NUMBER,
                        C_OBJECT_NUMBER,
                        self.get_table_name(object_names[0]),
                    )
                )
                for object_name in object_names[1:]:
                    fid.write(
                        "UNION SELECT %s, %s_%s as %s "
                        "FROM %s\n"
                        % (
                            C_IMAGE_NUMBER,
                            object_name,
                            M_NUMBER_OBJECT_NUMBER,
                            C_OBJECT_NUMBER,
                            self.get_table_name(object_name),
                        )
                    )
                fid.write(
                    ") N_INNER) N ON IT.%s = N.%s\n" % (C_IMAGE_NUMBER, C_IMAGE_NUMBER)
                )
                for i, object_name in enumerate(object_names):
                    fid.write(
                        "LEFT JOIN %s OT%d " % (self.get_table_name(object_name), i + 1)
                    )
                    fid.write(
                        "ON N.%s = OT%d.%s " % (C_IMAGE_NUMBER, i + 1, C_IMAGE_NUMBER)
                    )
                    fid.write(
                        "AND N.%s = OT%d.%s_%s\n"
                        % (C_OBJECT_NUMBER, i + 1, object_name, M_NUMBER_OBJECT_NUMBER)
                    )
            fid.write(
                "GROUP BY IT.Image_Metadata_Plate, " "IT.Image_Metadata_Well;\n\n" ""
            )

        if needs_close:
            fid.close()