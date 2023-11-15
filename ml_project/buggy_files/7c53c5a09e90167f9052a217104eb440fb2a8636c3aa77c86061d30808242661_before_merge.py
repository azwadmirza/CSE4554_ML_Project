    def get_experiment_table_statements(self, workspace):
        statements = []
        if self.db_type in (DB_MYSQL_CSV, DB_MYSQL):
            autoincrement = "AUTO_INCREMENT"
            need_text_size = True
        else:
            autoincrement = "AUTOINCREMENT"
            need_text_size = False
        create_experiment_table_statement = """
CREATE TABLE IF NOT EXISTS %s (
    experiment_id integer primary key %s,
    name text)""" % (
            T_EXPERIMENT,
            autoincrement,
        )
        statements.append(create_experiment_table_statement)
        if need_text_size:
            create_experiment_properties = (
                """
CREATE TABLE IF NOT EXISTS %(T_EXPERIMENT_PROPERTIES)s (
    experiment_id integer not null,
    object_name text not null,
    field text not null,
    value longtext,
    constraint %(T_EXPERIMENT_PROPERTIES)s_pk primary key
    (experiment_id, object_name(200), field(200)))"""
                % globals()
            )
        else:
            create_experiment_properties = (
                """
CREATE TABLE IF NOT EXISTS %(T_EXPERIMENT_PROPERTIES)s (
    experiment_id integer not null,
    object_name text not null,
    field text not null,
    value longtext,
    constraint %(T_EXPERIMENT_PROPERTIES)s_pk primary key (experiment_id, object_name, field))"""
                % globals()
            )

        statements.append(create_experiment_properties)
        insert_into_experiment_statement = """
INSERT INTO %s (name) values ('%s')""" % (
            T_EXPERIMENT,
            MySQLdb.escape_string(self.experiment_name.value).decode(),
        )
        statements.append(insert_into_experiment_statement)

        properties = self.get_property_file_text(workspace)
        for p in properties:
            for k, v in list(p.properties.items()):
                if isinstance(v, six.text_type):
                    v = v
                statement = """
INSERT INTO %s (experiment_id, object_name, field, value)
SELECT MAX(experiment_id), '%s', '%s', '%s' FROM %s""" % (
                    T_EXPERIMENT_PROPERTIES,
                    p.object_name,
                    MySQLdb.escape_string(k).decode(),
                    MySQLdb.escape_string(v).decode(),
                    T_EXPERIMENT,
                )
                statements.append(statement)

        experiment_columns = list(
            filter(
                lambda x: x[0] == cellprofiler_core.measurement.EXPERIMENT,
                workspace.pipeline.get_measurement_columns(),
            )
        )
        experiment_coldefs = [
            "%s %s"
            % (
                x[1],
                "TEXT"
                if x[2].startswith(cellprofiler_core.measurement.COLTYPE_VARCHAR)
                else x[2],
            )
            for x in experiment_columns
        ]
        create_per_experiment = """
CREATE TABLE %s (
%s)
""" % (
            self.get_table_name(cellprofiler_core.measurement.EXPERIMENT),
            ",\n".join(experiment_coldefs),
        )
        statements.append(create_per_experiment)
        column_names = []
        values = []
        for column in experiment_columns:
            ftr = column[1]
            column_names.append(ftr)
            if (
                len(column) > 3
                and column[3].get(
                    cellprofiler_core.measurement.MCA_AVAILABLE_POST_RUN, False
                )
            ) or not workspace.measurements.has_feature(
                cellprofiler_core.measurement.EXPERIMENT, ftr
            ):
                values.append("null")
                continue
            value = workspace.measurements.get_experiment_measurement(ftr)

            if column[2].startswith(cellprofiler_core.measurement.COLTYPE_VARCHAR):
                if isinstance(value, six.text_type):
                    value = value
                if self.db_type != DB_SQLITE:
                    value = MySQLdb.escape_string(value).decode()
                else:
                    value = value.replace("'", "''")
                value = "'" + value + "'"
            else:
                # Both MySQL and SQLite support blob literals of the style:
                # X'0123456789ABCDEF'
                #
                value = "X'" + "".join(["%02X" % ord(x) for x in value]) + "'"
            values.append(value)
        experiment_insert_statement = "INSERT INTO %s (%s) VALUES (%s)" % (
            self.get_table_name(cellprofiler_core.measurement.EXPERIMENT),
            ",".join(column_names),
            ",".join(values),
        )
        statements.append(experiment_insert_statement)
        return statements