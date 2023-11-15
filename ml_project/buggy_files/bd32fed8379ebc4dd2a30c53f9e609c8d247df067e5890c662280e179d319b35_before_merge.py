    def upgrade_settings(self, setting_values, variable_revision_number, module_name, from_matlab):
        if from_matlab and variable_revision_number == 2:
            setting_values = [
                setting_values[0],
                setting_values[1],
                setting_values[2],
                cellprofiler.setting.DO_NOT_USE,
                cellprofiler.setting.YES
            ]

            variable_revision_number = 3

        if from_matlab and variable_revision_number == 3:
            setting_values = list(setting_values)

            setting_values[2] = (D_MINIMUM if setting_values[2] == cellprofiler.setting.YES else D_NONE)

            variable_revision_number = 4

        if from_matlab and variable_revision_number == 4:
            if setting_values[2] == cellprofiler.setting.DO_NOT_USE:
                setting_values = (setting_values[:2] + [D_NONE] + setting_values[3:])

            from_matlab = False

            variable_revision_number = 1

        if (not from_matlab) and variable_revision_number == 1:
            #
            # Added other distance parents
            #
            if setting_values[2] == cellprofiler.setting.DO_NOT_USE:
                find_parent_distances = D_NONE
            else:
                find_parent_distances = setting_values[2]

            if setting_values[3].upper() == cellprofiler.setting.DO_NOT_USE.upper():
                wants_step_parent_distances = cellprofiler.setting.NO
            else:
                wants_step_parent_distances = cellprofiler.setting.YES

            setting_values = (setting_values[:2] + [
                find_parent_distances,
                setting_values[4],
                wants_step_parent_distances,
                setting_values[3]
            ])

            variable_revision_number = 2

        return setting_values, variable_revision_number, from_matlab