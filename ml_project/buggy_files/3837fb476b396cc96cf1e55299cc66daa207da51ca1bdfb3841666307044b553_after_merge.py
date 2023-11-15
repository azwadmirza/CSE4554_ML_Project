    def visible_settings(self):
        needs_default_output_directory = (
            self.db_type != DB_MYSQL
            or self.save_cpa_properties.value
            or self.create_workspace_file.value
        )
        # # # # # # # # # # # # # # # # # #
        #
        # DB type and connection info
        #
        # # # # # # # # # # # # # # # # # #
        result = [self.db_type, self.experiment_name]
        if not HAS_MYSQL_DB:
            result += [self.mysql_not_available]
        if self.db_type == DB_MYSQL:
            result += [self.db_name]
            result += [self.db_host]
            result += [self.db_user]
            result += [self.db_passwd]
            result += [self.test_connection_button]
        elif self.db_type == DB_SQLITE:
            result += [self.sqlite_file]
        result += [self.allow_overwrite]
        # # # # # # # # # # # # # # # # # #
        #
        # Table names
        #
        # # # # # # # # # # # # # # # # # #
        result += [self.want_table_prefix]
        if self.want_table_prefix.value:
            result += [self.table_prefix]
        # # # # # # # # # # # # # # # # # #
        #
        # CPA properties file
        #
        # # # # # # # # # # # # # # # # # #
        if self.save_cpa_properties.value:
            result += [
                self.divider_props
            ]  # Put divider here to make things easier to read
        result += [self.save_cpa_properties]
        if self.save_cpa_properties.value:
            if self.objects_choice != O_NONE and (
                self.separate_object_tables == OT_COMBINE
                or self.separate_object_tables == OT_VIEW
            ):
                result += [self.location_object]
            result += [self.wants_properties_image_url_prepend]
            if self.wants_properties_image_url_prepend:
                result += [self.properties_image_url_prepend]
            result += [
                self.properties_plate_type,
                self.properties_plate_metadata,
                self.properties_well_metadata,
                self.properties_export_all_image_defaults,
            ]
            if not self.properties_export_all_image_defaults:
                for group in self.image_groups:
                    if group.can_remove:
                        result += [group.divider]
                    result += [group.image_cols, group.wants_automatic_image_name]
                    if not group.wants_automatic_image_name:
                        result += [group.image_name]
                    result += [group.image_channel_colors]
                    if group.can_remove:
                        result += [group.remover]
                result += [self.add_image_button]
            result += [self.properties_wants_groups]
            if self.properties_wants_groups:
                for group in self.group_field_groups:
                    if group.can_remove:
                        result += [group.divider]
                    result += [group.group_name, group.group_statement]
                    if group.can_remove:
                        result += [group.remover]
                result += [self.add_group_field_button]
            result += [self.properties_wants_filters]
            if self.properties_wants_filters:
                result += [self.create_filters_for_plates]
                for group in self.filter_field_groups:
                    result += [group.filter_name, group.filter_statement]
                    if group.can_remove:
                        result += [group.remover]
                    result += [group.divider]
                result += [self.add_filter_field_button]

            result += [self.properties_classification_type]
            result += [self.properties_class_table_name]

        if (
            self.save_cpa_properties.value or self.create_workspace_file.value
        ):  # Put divider here to make things easier to read
            result += [self.divider_props_wkspace]

        result += [self.create_workspace_file]
        if self.create_workspace_file:
            for workspace_group in self.workspace_measurement_groups:
                result += self.workspace_visible_settings(workspace_group)
                if workspace_group.can_remove:
                    result += [workspace_group.remove_button]
            result += [self.add_workspace_measurement_button]

        if (
            self.create_workspace_file.value
        ):  # Put divider here to make things easier to read
            result += [self.divider_wkspace]

        if needs_default_output_directory:
            result += [self.directory]

        # # # # # # # # # # # # # # # # # #
        #
        # Aggregations
        #
        # # # # # # # # # # # # # # # # # #
        result += [self.wants_agg_mean, self.wants_agg_median, self.wants_agg_std_dev]
        if self.db_type != DB_SQLITE:
            # We don't write per-well tables to SQLite yet.
            result += [
                self.wants_agg_mean_well,
                self.wants_agg_median_well,
                self.wants_agg_std_dev_well,
            ]
        # # # # # # # # # # # # # # # # # #
        #
        # Table choices (1 / separate object tables, etc)
        #
        # # # # # # # # # # # # # # # # # #
        result += [self.objects_choice]
        if self.objects_choice == O_SELECT:
            result += [self.objects_list]
        result += [self.wants_relationship_table_setting]
        if self.objects_choice != O_NONE:
            result += [self.separate_object_tables]

        # # # # # # # # # # # # # # # # # #
        #
        # Misc (column size + image thumbnails)
        #
        # # # # # # # # # # # # # # # # # #

        result += [self.max_column_size]
        if self.db_type in (DB_MYSQL, DB_SQLITE):
            result += [self.want_image_thumbnails]
            if self.want_image_thumbnails:
                result += [
                    self.thumbnail_image_names,
                    self.auto_scale_thumbnail_intensities,
                ]
        return result