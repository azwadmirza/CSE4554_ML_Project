    def settings(self):
        result = [
            self.db_type,
            self.db_name,
            self.want_table_prefix,
            self.table_prefix,
            self.sql_file_prefix,
            self.directory,
            self.save_cpa_properties,
            self.db_host,
            self.db_user,
            self.db_passwd,
            self.sqlite_file,
            self.wants_agg_mean,
            self.wants_agg_median,
            self.wants_agg_std_dev,
            self.wants_agg_mean_well,
            self.wants_agg_median_well,
            self.wants_agg_std_dev_well,
            self.objects_choice,
            self.objects_list,
            self.max_column_size,
            self.separate_object_tables,
            self.properties_image_url_prepend,
            self.want_image_thumbnails,
            self.thumbnail_image_names,
            self.auto_scale_thumbnail_intensities,
            self.properties_plate_type,
            self.properties_plate_metadata,
            self.properties_well_metadata,
            self.properties_export_all_image_defaults,
            self.image_group_count,
            self.group_field_count,
            self.filter_field_count,
            self.workspace_measurement_count,
            self.experiment_name,
            self.location_object,
            self.properties_class_table_name,
            self.wants_relationship_table_setting,
            self.allow_overwrite,
            self.wants_properties_image_url_prepend,
            self.properties_classification_type,
        ]

        # Properties: Image groups
        for group in self.image_groups:
            result += [
                group.image_cols,
                group.wants_automatic_image_name,
                group.image_name,
                group.image_channel_colors,
            ]
        result += [self.properties_wants_groups]

        # Properties: Grouping fields
        for group in self.group_field_groups:
            result += [group.group_name, group.group_statement]

        # Properties: Filter fields
        result += [self.properties_wants_filters, self.create_filters_for_plates]
        for group in self.filter_field_groups:
            result += [group.filter_name, group.filter_statement]

        # Workspace settings
        result += [self.create_workspace_file]
        for group in self.workspace_measurement_groups:
            result += [
                group.measurement_display,
                group.x_measurement_type,
                group.x_object_name,
                group.x_measurement_name,
                group.x_index_name,
                group.y_measurement_type,
                group.y_object_name,
                group.y_measurement_name,
                group.y_index_name,
            ]

        return result