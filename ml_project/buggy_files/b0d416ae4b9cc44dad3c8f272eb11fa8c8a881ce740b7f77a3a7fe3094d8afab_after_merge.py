    def write_data_to_db(self, workspace, post_group=False, image_number=None):
        """Write the data in the measurements out to the database
        workspace - contains the measurements
        mappings  - map a feature name to a column name
        image_number - image number for primary database key. Defaults to current.
        """
        if self.show_window:
            disp_header = ["Table", "Statement"]
            disp_columns = []
        try:
            zeros_for_nan = False
            measurements = workspace.measurements
            assert isinstance(measurements, Measurements)
            pipeline = workspace.pipeline
            image_set_list = workspace.image_set_list
            measurement_cols = self.get_pipeline_measurement_columns(
                pipeline, image_set_list
            )
            mapping = self.get_column_name_mappings(pipeline, image_set_list)

            ###########################################
            #
            # The image table
            #
            ###########################################
            if image_number is None:
                image_number = measurements.image_set_number

            image_row = []
            if not post_group:
                image_row += [(image_number, "integer", C_IMAGE_NUMBER,)]
            feature_names = set(measurements.get_feature_names("Image"))
            for m_col in measurement_cols:
                if m_col[0] != "Image":
                    continue
                if not self.should_write(m_col, post_group):
                    continue
                #
                # Skip if feature name not in measurements. This
                # can happen if image set gets aborted or for some legacy
                # measurement files.
                #
                if m_col[1] not in feature_names:
                    continue
                feature_name = "%s_%s" % ("Image", m_col[1])
                value = measurements.get_measurement("Image", m_col[1], image_number)
                if isinstance(value, numpy.ndarray):
                    value = value[0]
                if (
                    isinstance(value, float)
                    and not numpy.isfinite(value)
                    and zeros_for_nan
                ):
                    value = 0
                image_row.append((value, m_col[2], feature_name))
            #
            # Aggregates for the image table
            #
            agg_dict = measurements.compute_aggregate_measurements(
                image_number, self.agg_names
            )
            agg_columns = self.get_aggregate_columns(
                pipeline, image_set_list, post_group
            )
            image_row += [
                (agg_dict[agg[3]], COLTYPE_FLOAT, agg[3]) for agg in agg_columns
            ]

            #
            # Delete any prior data for this image
            #
            # Useful if you rerun a partially-complete batch
            #
            if not post_group:
                stmt = "DELETE FROM %s WHERE %s=%d" % (
                    self.get_table_name("Image"),
                    C_IMAGE_NUMBER,
                    image_number,
                )
                execute(self.cursor, stmt, return_result=False)
                #
                # Delete relationships as well.
                #
                if self.wants_relationship_table:
                    for col in (COL_IMAGE_NUMBER1, COL_IMAGE_NUMBER2):
                        stmt = "DELETE FROM %s WHERE %s=%d" % (
                            self.get_table_name(T_RELATIONSHIPS),
                            col,
                            image_number,
                        )
                        execute(self.cursor, stmt, return_result=False)

            ########################################
            #
            # Object tables
            #
            ########################################
            object_names = self.get_object_names(pipeline, image_set_list)
            if len(object_names) > 0:
                if self.separate_object_tables == OT_COMBINE:
                    data = [(OBJECT, object_names)]
                else:
                    data = [
                        (object_name, [object_name]) for object_name in object_names
                    ]
                for table_object_name, object_list in data:
                    table_name = self.get_table_name(table_object_name)
                    columns = [
                        column
                        for column in measurement_cols
                        if column[0] in object_list
                        and self.should_write(column, post_group)
                    ]
                    if post_group and len(columns) == 0:
                        continue
                    max_count = 0
                    for object_name in object_list:
                        ftr_count = "Count_%s" % object_name
                        count = measurements.get_measurement(
                            "Image", ftr_count, image_number
                        )
                        max_count = max(max_count, int(count))
                    column_values = []
                    for column in columns:
                        object_name, feature, coltype = column[:3]
                        values = measurements.get_measurement(
                            object_name, feature, image_number
                        )

                        if len(values) < max_count:
                            values = list(values) + [None] * (max_count - len(values))
                        values = [
                            None
                            if v is None or numpy.isnan(v) or numpy.isinf(v)
                            else str(v)
                            for v in values
                        ]
                        column_values.append(values)
                    object_cols = []
                    if not post_group:
                        object_cols += [C_IMAGE_NUMBER]
                    if table_object_name == OBJECT:
                        object_number_column = C_OBJECT_NUMBER
                        if not post_group:
                            object_cols += [object_number_column]
                        object_numbers = numpy.arange(1, max_count + 1)
                    else:
                        object_number_column = "_".join(
                            (object_name, M_NUMBER_OBJECT_NUMBER)
                        )
                        object_numbers = measurements.get_measurement(
                            object_name, M_NUMBER_OBJECT_NUMBER, image_number
                        )

                    object_cols += [
                        mapping["%s_%s" % (column[0], column[1])] for column in columns
                    ]
                    object_rows = []
                    for j in range(max_count):
                        if not post_group:
                            object_row = [image_number]
                            if table_object_name == OBJECT:
                                # the object number
                                object_row.append(object_numbers[j])
                        else:
                            object_row = []

                        for column, values in zip(columns, column_values):
                            object_name, feature, coltype = column[:3]
                            object_row.append(values[j])
                        if post_group:
                            object_row.append(object_numbers[j])
                        object_rows.append(object_row)
                    #
                    # Delete any prior data for this image
                    #
                    if not post_group:
                        stmt = "DELETE FROM %s WHERE %s=%d" % (
                            table_name,
                            C_IMAGE_NUMBER,
                            image_number,
                        )

                        execute(self.cursor, stmt, return_result=False)
                        #
                        # Write the object table data
                        #
                        stmt = "INSERT INTO %s (%s) VALUES (%s)" % (
                            table_name,
                            ",".join(object_cols),
                            ",".join(["%s"] * len(object_cols)),
                        )
                    else:
                        stmt = (
                            ("UPDATE %s SET\n" % table_name)
                            + (",\n".join(["  %s=%%s" % c for c in object_cols]))
                            + ("\nWHERE %s = %d" % (C_IMAGE_NUMBER, image_number))
                            + ("\nAND %s = %%s" % object_number_column)
                        )

                    if self.db_type == DB_MYSQL:
                        # Write 25 rows at a time (to get under the max_allowed_packet limit)
                        for i in range(0, len(object_rows), 25):
                            my_rows = object_rows[i : min(i + 25, len(object_rows))]
                            self.cursor.executemany(stmt, my_rows)
                        if self.show_window and len(object_rows) > 0:
                            disp_columns.append(
                                (
                                    table_name,
                                    self.truncate_string_for_display(
                                        stmt % tuple(my_rows[0])
                                    ),
                                )
                            )
                    else:
                        for row in object_rows:
                            row = ["NULL" if x is None else x for x in row]
                            row_stmt = stmt % tuple(row)
                            execute(self.cursor, row_stmt, return_result=False)
                        if self.show_window and len(object_rows) > 0:
                            disp_columns.append(
                                (table_name, self.truncate_string_for_display(row_stmt))
                            )

            image_table = self.get_table_name("Image")
            replacement = "%s" if self.db_type == DB_MYSQL else "?"
            image_row_values = [
                None
                if field[0] is None
                else None
                if (
                    (field[1] == COLTYPE_FLOAT)
                    and (numpy.isnan(field[0]) or numpy.isinf(field[0]))
                )
                else float(field[0])
                if (field[1] == COLTYPE_FLOAT)
                else int(field[0])
                if (field[1] == "integer")
                else field[0]
                for field in image_row
            ]
            if len(image_row) > 0:
                if not post_group:
                    stmt = "INSERT INTO %s (%s) VALUES (%s)" % (
                        image_table,
                        ",".join(
                            [mapping[colname] for val, dtype, colname in image_row]
                        ),
                        ",".join([replacement] * len(image_row)),
                    )
                else:
                    stmt = (
                        ("UPDATE %s SET\n" % image_table)
                        + ",\n".join(
                            [
                                "  %s = %s" % (mapping[colname], replacement)
                                for val, dtype, colname in image_row
                            ]
                        )
                        + ("\nWHERE %s = %d" % (C_IMAGE_NUMBER, image_number))
                    )
                execute(self.cursor, stmt, image_row_values, return_result=False)

            if self.show_window:
                disp_columns.append(
                    (
                        image_table,
                        self.truncate_string_for_display(
                            stmt + " VALUES(%s)" % ",".join(map(str, image_row_values))
                        )
                        if len(image_row) > 0
                        else "",
                    )
                )

            if self.wants_relationship_table:
                #
                # Relationships table - for SQLite, check for previous existence
                # but for MySQL use REPLACE INTO to do the same
                #
                rtbl_name = self.get_table_name(T_RELATIONSHIPS)
                columns = [
                    COL_RELATIONSHIP_TYPE_ID,
                    COL_IMAGE_NUMBER1,
                    COL_OBJECT_NUMBER1,
                    COL_IMAGE_NUMBER2,
                    COL_OBJECT_NUMBER2,
                ]
                if self.db_type == DB_SQLITE:
                    stmt = "INSERT INTO %s (%s, %s, %s, %s, %s) " % tuple(
                        [rtbl_name] + columns
                    )
                    stmt += " SELECT %d, %d, %d, %d, %d WHERE NOT EXISTS "
                    stmt += "(SELECT 'x' FROM %s WHERE " % rtbl_name
                    stmt += " AND ".join(["%s = %%d" % col for col in columns]) + ")"
                else:
                    stmt = "REPLACE INTO %s (%s, %s, %s, %s, %s) " % tuple(
                        [rtbl_name] + columns
                    )
                    stmt += "VALUES (%s, %s, %s, %s, %s)"
                for (
                    module_num,
                    relationship,
                    object_name1,
                    object_name2,
                    when,
                ) in pipeline.get_object_relationships():
                    if post_group != (when == MCA_AVAILABLE_POST_GROUP):
                        continue
                    r = measurements.get_relationships(
                        module_num,
                        relationship,
                        object_name1,
                        object_name2,
                        image_numbers=[image_number],
                    )
                    rt_id = self.get_relationship_type_id(
                        workspace, module_num, relationship, object_name1, object_name2
                    )
                    if self.db_type == DB_MYSQL:
                        # max_allowed_packet is 16 MB by default
                        # 8 x 10 = 80/row -> 200K rows
                        row_values = [(rt_id, i1, o1, i2, o2) for i1, o1, i2, o2 in r]
                        self.cursor.executemany(stmt, row_values)
                        if self.show_window and len(r) > 0:
                            disp_columns.append(
                                (
                                    rtbl_name,
                                    self.truncate_string_for_display(
                                        stmt % tuple(row_values[0])
                                    ),
                                )
                            )
                    else:
                        for i1, o1, i2, o2 in r:
                            row = (rt_id, i1, o1, i2, o2, rt_id, i1, o1, i2, o2)
                            row_stmt = stmt % tuple(row)
                            execute(self.cursor, row_stmt, return_result=False)
                        if self.show_window and len(r) > 0:
                            disp_columns.append(
                                (rtbl_name, self.truncate_string_for_display(row_stmt))
                            )

            if self.show_window:
                workspace.display_data.header = disp_header
                workspace.display_data.columns = disp_columns

            ###########################################
            #
            # The experiment table
            #
            ###########################################
            stmt = "UPDATE %s SET %s='%s'" % (
                self.get_table_name(EXPERIMENT),
                M_MODIFICATION_TIMESTAMP,
                datetime.datetime.now().isoformat(),
            )
            execute(self.cursor, stmt, return_result=False)

            self.connection.commit()
        except:
            logging.error("Failed to write measurements to database", exc_info=True)
            self.connection.rollback()
            raise