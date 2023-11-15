    def validate_module(self, pipeline):
        if self.want_table_prefix.value:
            if not re.match("^[A-Za-z][A-Za-z0-9_]+$", self.table_prefix.value):
                raise cellprofiler_core.setting.ValidationError(
                    "Invalid table prefix", self.table_prefix
                )

        if self.db_type == DB_MYSQL:
            if not re.match("^[A-Za-z0-9_]+$", self.db_name.value):
                raise cellprofiler_core.setting.ValidationError(
                    "The database name has invalid characters", self.db_name
                )
        elif self.db_type == DB_SQLITE:
            if not re.match("^[A-Za-z0-9_].*$", self.sqlite_file.value):
                raise cellprofiler_core.setting.ValidationError(
                    "The sqlite file name has invalid characters", self.sqlite_file
                )

        if self.db_type == DB_MYSQL:
            if not re.match("^[A-Za-z0-9_].*$", self.db_host.value):
                raise cellprofiler_core.setting.ValidationError(
                    "The database host name has invalid characters", self.db_host
                )
            if not re.match("^[A-Za-z0-9_]+$", self.db_user.value):
                raise cellprofiler_core.setting.ValidationError(
                    "The database user name has invalid characters", self.db_user
                )
        else:
            if not re.match("^[A-Za-z][A-Za-z0-9_]+$", self.sql_file_prefix.value):
                raise cellprofiler_core.setting.ValidationError(
                    "Invalid SQL file prefix", self.sql_file_prefix
                )

        if self.objects_choice == O_SELECT:
            self.objects_list.load_choices(pipeline)
            if len(self.objects_list.choices) == 0:
                raise cellprofiler_core.setting.ValidationError(
                    "Please choose at least one object", self.objects_choice
                )

        if self.save_cpa_properties:
            if self.properties_plate_metadata == NONE_CHOICE and (
                self.properties_wants_filters.value
                and self.create_filters_for_plates.value
            ):
                raise cellprofiler_core.setting.ValidationError(
                    "You must specify the plate metadata",
                    self.create_filters_for_plates,
                )

        if self.want_image_thumbnails:
            if not self.thumbnail_image_names.get_selections():
                raise cellprofiler_core.setting.ValidationError(
                    "Please choose at least one image", self.thumbnail_image_names
                )

        if self.want_table_prefix:
            max_char = 64
            table_name_lengths = [len(self.table_prefix.value + "Per_Image")]
            table_name_lengths += (
                [len(self.table_prefix.value + "Per_Object")]
                if self.objects_choice != O_NONE
                and self.separate_object_tables.value in (OT_COMBINE, OT_VIEW)
                else []
            )
            table_name_lengths += (
                [
                    len(self.table_prefix.value + "Per_" + x)
                    for x in self.objects_list.value.split(",")
                ]
                if self.objects_choice != O_NONE
                and self.separate_object_tables == OT_PER_OBJECT
                else []
            )
            if numpy.any(numpy.array(table_name_lengths) > max_char):
                msg = (
                    "A table name exceeds the %d character allowed by MySQL.\n"
                    % max_char
                )
                msg += "Please shorten the prefix if using a single object table,\n"
                msg += "and/or the object name if using separate tables."
                raise cellprofiler_core.setting.ValidationError(msg, self.table_prefix)