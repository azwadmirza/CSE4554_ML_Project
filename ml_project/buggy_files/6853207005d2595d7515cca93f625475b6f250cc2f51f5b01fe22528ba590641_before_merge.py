    def upgrade_settings(self, setting_values, variable_revision_number,
                         module_name, from_matlab):
        if from_matlab and variable_revision_number == 4:
            # Added OFF_REMOVE_ROWS_AND_COLUMNS
            new_setting_values = list(setting_values)
            new_setting_values.append(cps.NO)
            variable_revision_number = 5
        if from_matlab and variable_revision_number == 5:
            # added image mask source, cropping mask source and reworked
            # the shape to add SH_IMAGE and SH_CROPPING
            new_setting_values = list(setting_values)
            new_setting_values.extend([cps.NONE, cps.NONE, cps.NONE])
            shape = setting_values[OFF_SHAPE]
            if shape not in (SH_ELLIPSE, SH_RECTANGLE):
                # the "shape" is the name of some image file. If it
                # starts with Cropping, then it's the crop mask of
                # some other image
                if shape.startswith('Cropping'):
                    new_setting_values[OFF_CROPPING_MASK_SOURCE] = \
                        shape[len('Cropping'):]
                    new_setting_values[OFF_SHAPE] = SH_CROPPING
                else:
                    new_setting_values[OFF_IMAGE_MASK_SOURCE] = shape
                    new_setting_values[OFF_SHAPE] = SH_IMAGE
            if new_setting_values[OFF_REMOVE_ROWS_AND_COLUMNS] == cps.YES:
                new_setting_values[OFF_REMOVE_ROWS_AND_COLUMNS] = RM_EDGES
            setting_values = new_setting_values
            variable_revision_number = 2
            from_matlab = False

        if (not from_matlab) and variable_revision_number == 1:
            # Added ability to crop objects
            new_setting_values = list(setting_values)
            new_setting_values.append(cps.NONE)
            variable_revision_number = 2

        if variable_revision_number == 2 and not from_matlab:
            # minor - "Cropping" changed to "Previous cropping"
            setting_values = list(setting_values)
            if setting_values[OFF_SHAPE] == "Cropping":
                setting_values[OFF_SHAPE] = SH_CROPPING
            #
            # Individually changed to "every"
            #
            if setting_values[OFF_INDIVIDUAL_OR_ONCE] == "Individually":
                setting_values[OFF_INDIVIDUAL_OR_ONCE] = IO_INDIVIDUALLY

            setting_values = setting_values[:10] + setting_values[11:]

            variable_revision_number = 3

        return setting_values, variable_revision_number, from_matlab