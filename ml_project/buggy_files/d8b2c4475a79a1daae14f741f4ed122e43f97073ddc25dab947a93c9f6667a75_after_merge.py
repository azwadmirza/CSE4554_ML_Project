    def upgrade_settings(self, setting_values, variable_revision_number, module_name):

        DIR_DEFAULT_OUTPUT = "Default output folder"
        DIR_DEFAULT_IMAGE = "Default input folder"

        if variable_revision_number == 6:
            # Append default values for store_csvs, db_host, db_user,
            #  db_passwd, and sqlite_file to update to revision 7
            setting_values += [False, "imgdb01", "cpuser", "", "DefaultDB.db"]
            variable_revision_number = 7

        if variable_revision_number == 7:
            # Added ability to selectively turn on aggregate measurements
            # which were all automatically calculated in version 7
            setting_values = setting_values + [True, True, True]
            variable_revision_number = 8

        if variable_revision_number == 8:
            # Made it possible to choose objects to save
            #
            setting_values += [O_ALL, ""]
            variable_revision_number = 9

        if variable_revision_number == 9:
            # Added aggregate per well choices
            #
            setting_values = (
                setting_values[:-2] + [False, False, False] + setting_values[-2:]
            )
            variable_revision_number = 10

        if variable_revision_number == 10:
            #
            # Added a directory choice instead of a checkbox
            #
            if setting_values[5] == "No" or setting_values[6] == ".":
                directory_choice = DIR_DEFAULT_OUTPUT
            elif setting_values[6] == "&":
                directory_choice = DIR_DEFAULT_IMAGE
            else:
                directory_choice = DIR_CUSTOM
            setting_values = (
                setting_values[:5] + [directory_choice] + setting_values[6:]
            )
            variable_revision_number = 11

        if variable_revision_number == 11:
            #
            # Added separate "database type" of CSV files and removed
            # "store_csvs" setting
            #
            db_type = setting_values[0]
            store_csvs = setting_values[8] == "Yes"
            if db_type == DB_MYSQL and store_csvs:
                db_type = DB_MYSQL_CSV
            setting_values = [db_type] + setting_values[1:8] + setting_values[9:]
            variable_revision_number = 12

        if variable_revision_number == 12:
            #
            # Added maximum column size
            #
            setting_values = setting_values + ["64"]
            variable_revision_number = 13

        if variable_revision_number == 13:
            #
            # Added single/multiple table choice
            #
            setting_values = setting_values + [OT_COMBINE]
            variable_revision_number = 14

        if variable_revision_number == 14:
            #
            # Combined directory_choice and output_folder into directory
            #
            dir_choice, custom_directory = setting_values[5:7]
            if dir_choice in (DIR_CUSTOM, DIR_CUSTOM_WITH_METADATA):
                if custom_directory.startswith("."):
                    dir_choice = (
                        cellprofiler_core.preferences.DEFAULT_OUTPUT_SUBFOLDER_NAME
                    )
                elif custom_directory.startswith("&"):
                    dir_choice = (
                        cellprofiler_core.preferences.DEFAULT_INPUT_SUBFOLDER_NAME
                    )
                    custom_directory = "." + custom_directory[1:]
                else:
                    dir_choice = cellprofiler_core.preferences.ABSOLUTE_FOLDER_NAME
            directory = cellprofiler_core.setting.DirectoryPath.static_join_string(
                dir_choice, custom_directory
            )
            setting_values = setting_values[:5] + [directory] + setting_values[7:]
            variable_revision_number = 15

        setting_values = list(setting_values)
        setting_values[OT_IDX] = OT_DICTIONARY.get(
            setting_values[OT_IDX], setting_values[OT_IDX]
        )


        if variable_revision_number == 15:
            #
            # Added 3 new args: url_prepend and thumbnail options
            #
            setting_values = setting_values + ["", "No", ""]
            variable_revision_number = 16

        if variable_revision_number == 16:
            #
            # Added binary choice for auto-scaling thumbnail intensities
            #
            setting_values = setting_values + ["No"]
            variable_revision_number = 17

        if variable_revision_number == 17:
            #
            # Added choice for plate type in properties file
            #
            setting_values = setting_values + [NONE_CHOICE]
            variable_revision_number = 18

        if variable_revision_number == 18:
            #
            # Added choices for plate and well metadata in properties file
            #
            setting_values = setting_values + [NONE_CHOICE, NONE_CHOICE]
            variable_revision_number = 19

        if variable_revision_number == 19:
            #
            # Added configuration of image information, groups, filters in properties file
            #
            setting_values = setting_values + [
                "Yes",
                "1",
                "1",
                "0",
            ]  # Hidden counts
            setting_values = setting_values + [
                "None",
                "Yes",
                "None",
                "gray",
            ]  # Image info
            setting_values = setting_values + [
                "No",
                "",
                "ImageNumber, Image_Metadata_Plate, Image_Metadata_Well",
            ]  # Group specifications
            setting_values = setting_values + [
                "No",
                "No",
            ]  # Filter specifications
            variable_revision_number = 20

        if variable_revision_number == 20:
            #
            # Added configuration of workspace file
            #
            setting_values = (
                    setting_values[:SETTING_WORKSPACE_GROUP_COUNT_PRE_V28]
                + ["1"]
                + setting_values[SETTING_WORKSPACE_GROUP_COUNT_PRE_V28:]
            )  # workspace_measurement_count
            setting_values += ["No"]  # create_workspace_file
            setting_values += [
                W_SCATTERPLOT,  # measurement_display
                cellprofiler_core.measurement.IMAGE,
                cellprofiler_core.measurement.IMAGE,
                "",
                C_IMAGE_NUMBER,
                # x_measurement_type, x_object_name, x_measurement_name, x_index_name
                cellprofiler_core.measurement.IMAGE,
                cellprofiler_core.measurement.IMAGE,
                "",
                C_IMAGE_NUMBER,
            ]  # y_measurement_type, y_object_name, y_measurement_name, y_index_name
            variable_revision_number = 21

        if variable_revision_number == 21:
            #
            # Added experiment name and location object
            #
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V21]
                + ["MyExpt", "None"]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V21:]
            )
            variable_revision_number = 22

        if variable_revision_number == 22:
            #
            # Added class table properties field
            #
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V22]
                + [""]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V22:]
            )
            variable_revision_number = 23

        if variable_revision_number == 23:
            #
            # Added wants_relationships_table
            #
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V23]
                + ["No"]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V23:]
            )
            variable_revision_number = 24

        if variable_revision_number == 24:
            #
            # Added allow_overwrite
            #
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V24]
                + [OVERWRITE_DATA]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V24:]
            )
            variable_revision_number = 25

        if variable_revision_number == 25:
            #
            # added wants_properties_image_url_prepend setting
            #
            wants_urls = (
                len(setting_values[SETTING_OFFSET_PROPERTIES_IMAGE_URL_PREPEND_V26]) > 0
            )
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V25]
                + ["Yes" if wants_urls else "No"]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V25:]
            )
            variable_revision_number = 26

        # Added view creation to object table settings
        setting_values[OT_IDX] = OT_DICTIONARY.get(
            setting_values[OT_IDX], setting_values[OT_IDX]
        )

        if variable_revision_number == 26:
            #
            # added classification_type setting
            #
            setting_values = (
                setting_values[:SETTING_FIXED_SETTING_COUNT_V26]
                + [CT_OBJECT]
                + setting_values[SETTING_FIXED_SETTING_COUNT_V26:]
            )
            variable_revision_number = 27

        if variable_revision_number == 27:
            print("Upgrading setting ", setting_values[0])
            #
            # Removed MySQL/CSV Mode
            #
            del setting_values[4]
            if setting_values[0] == DB_MYSQL_CSV:
                setting_values[0] = DB_SQLITE
                print("WARNING: ExportToDatabase MySQL/CSV mode has been "
                      "deprecated and removed.\nThis module has been converted "
                      "to produce an SQLite database.\n"
                      "ExportToSpreadsheet should be used if you need to "
                      "generate CSV files.")
            variable_revision_number = 28

        # Standardize input/output directory name references
        SLOT_DIRCHOICE = 4
        directory = setting_values[SLOT_DIRCHOICE]
        directory = cellprofiler_core.setting.DirectoryPath.upgrade_setting(directory)
        setting_values[SLOT_DIRCHOICE] = directory

        return setting_values, variable_revision_number