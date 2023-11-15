    def upgrade_settings(self, setting_values, variable_revision_number, module_name, from_matlab):
        if variable_revision_number == 1:
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

        if variable_revision_number == 2:
            setting_values = [setting_values[1], setting_values[0]] + setting_values[2:]

            variable_revision_number = 3

        return setting_values, variable_revision_number, from_matlab