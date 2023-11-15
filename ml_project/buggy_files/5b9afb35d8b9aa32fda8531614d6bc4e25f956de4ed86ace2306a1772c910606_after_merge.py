    def upgrade_settings(self, setting_values, variable_revision_number,
                         module_name, from_matlab):
        if (from_matlab and module_name == 'Subtract' and variable_revision_number == 3):
            subtract_image_name, basic_image_name, resulting_image_name, \
                multiply_factor_1, multiply_factor_2, truncate = setting_values
            setting_values = [O_SUBTRACT,
                              1,  # exponent
                              1,  # post-multiply factor
                              0,  # addend
                              truncate,  # truncate low
                              cellprofiler.setting.NO,  # truncate high
                              resulting_image_name,
                              basic_image_name,
                              multiply_factor_2,
                              subtract_image_name,
                              multiply_factor_1]
            module_name = 'ImageMath'
            from_matlab = False
            variable_revision_number = 1
        if (from_matlab and module_name == 'Combine' and variable_revision_number == 3):
            names_and_weights = [
                (name, weight)
                for name, weight in zip(setting_values[:3],
                                        setting_values[4:])
                if name.lower() != cellprofiler.setting.DO_NOT_USE.lower()]

            multiplier = 1.0 / sum([float(weight)
                                    for name, weight in names_and_weights])
            output_image = setting_values[3]
            setting_values = [O_ADD,  # Operation
                              "1",  # Exponent
                              str(multiplier),  # Post-operation multiplier
                              "0",  # Post-operation offset
                              cellprofiler.setting.NO,  # Truncate low
                              cellprofiler.setting.NO,  # Truncate high
                              output_image]
            for name, weight in names_and_weights:
                setting_values += [name, weight]
            module_name = 'ImageMath'
            variable_revision_number = 1
            from_matlab = False
        if (from_matlab and module_name == 'InvertIntensity' and variable_revision_number == 1):
            image_name, output_image = setting_values
            setting_values = [image_name, cellprofiler.setting.DO_NOT_USE, cellprofiler.setting.DO_NOT_USE,
                              'Invert',
                              1, 1, 1, 1, 1, cellprofiler.setting.NO, cellprofiler.setting.NO, output_image]
            module_name = 'ImageMath'
            variable_revision_number = 2
        if (from_matlab and module_name == 'Multiply' and variable_revision_number == 1):
            image1, image2, output_image = setting_values
            setting_values = [image1, image2, cellprofiler.setting.DO_NOT_USE,
                              'Multiply', 1, 1, 1, 1, 1, cellprofiler.setting.NO, cellprofiler.setting.NO,
                              output_image]
            module_name = 'ImageMath'
            variable_revision_number = 2

        if (from_matlab and variable_revision_number == 1 and module_name == 'ImageMath'):
            image_names = [setting_values[1]]
            input_factors = [float(setting_values[4])]
            operation = setting_values[3]
            factors = []
            # The user could type in a constant for the second image name
            try:
                factors += [float(setting_values[2]) *
                            float(setting_values[5])]
            except ValueError:
                if setting_values[2] != cellprofiler.setting.DO_NOT_USE:
                    image_names += [setting_values[2]]
                    input_factors += [float(setting_values[5])]
            exponent = 1.0
            multiplier = 1.0
            addend = 0
            wants_truncate_low = setting_values[6]
            wants_truncate_high = setting_values[7]
            output_image_name = setting_values[0]
            old_operation = operation
            if operation == O_DIVIDE and len(factors):
                multiplier /= numpy.product(factors)
            elif operation == O_MULTIPLY and len(factors):
                multiplier *= numpy.product(factors)
            elif operation == O_ADD and len(factors):
                addend = numpy.sum(factors)
            elif operation == O_SUBTRACT:
                addend = -numpy.sum(factors)
            setting_values = [operation, exponent, multiplier, addend,
                              wants_truncate_low, wants_truncate_high,
                              output_image_name]
            if operation == O_COMPLEMENT:
                image_names = image_names[:1]
                input_factors = input_factors[:1]
            elif old_operation in (O_ADD, O_SUBTRACT, O_MULTIPLY, O_DIVIDE):
                if len(image_names) < 2:
                    setting_values[0] = O_NONE
                image_names = image_names[:2]
                input_factors = input_factors[:2]
            for image_name, input_factor in zip(image_names, input_factors):
                setting_values += [image_name, input_factor]
            from_matlab = False
            variable_revision_number = 1

        if (from_matlab and variable_revision_number == 2 and module_name == 'ImageMath'):
            image_names = [setting_values[0]]
            input_factors = [float(setting_values[4])]
            operation = setting_values[3]
            factors = []
            for i in range(1, 3 if operation == O_COMBINE else 2):
                # The user could type in a constant for the second or third image name
                try:
                    factors += [float(setting_values[i]) * float(setting_values[i + 4])]
                except ValueError:
                    if setting_values[i] != cellprofiler.setting.DO_NOT_USE:
                        image_names += [setting_values[i]]
                        input_factors += [float(setting_values[i + 4])]

            exponent = float(setting_values[7])
            multiplier = float(setting_values[8])
            addend = 0
            wants_truncate_low = setting_values[9]
            wants_truncate_high = setting_values[10]
            output_image_name = setting_values[11]
            old_operation = operation
            if operation == O_COMBINE:
                addend = numpy.sum(factors)
                operation = O_ADD
            elif operation == O_DIVIDE and len(factors):
                multiplier /= numpy.product(factors)
            elif operation == O_MULTIPLY and len(factors):
                multiplier *= numpy.product(factors)
            elif operation == O_ADD and len(factors):
                addend = numpy.sum(factors)
            elif operation == O_SUBTRACT:
                addend = -numpy.sum(factors)
            setting_values = [operation, exponent, multiplier, addend,
                              wants_truncate_low, wants_truncate_high,
                              output_image_name]
            if operation in (O_INVERT, O_LOG_TRANSFORM):
                image_names = image_names[:1]
                input_factors = input_factors[:1]
            elif old_operation in (O_ADD, O_SUBTRACT, O_MULTIPLY, O_DIVIDE,
                                   O_AVERAGE):
                if len(image_names) < 2:
                    setting_values[0] = O_NONE
                image_names = image_names[:2]
                input_factors = input_factors[:2]
                # Fix for variable_revision_number 2: subtract reversed operands
                if old_operation == O_SUBTRACT:
                    image_names.reverse()
                    input_factors.reverse()
            for image_name, input_factor in zip(image_names, input_factors):
                setting_values += [image_name, input_factor]
            from_matlab = False
            variable_revision_number = 1
        if (not from_matlab) and variable_revision_number == 1:
            # added image_or_measurement and measurement
            new_setting_values = setting_values[:FIXED_SETTING_COUNT_1]
            for i in range(FIXED_SETTING_COUNT_1, len(setting_values),
                           IMAGE_SETTING_COUNT_1):
                new_setting_values += [IM_IMAGE, setting_values[i],
                                       setting_values[i + 1], ""]
            setting_values = new_setting_values
            variable_revision_number = 2
        if (not from_matlab) and variable_revision_number == 2:
            # added the ability to ignore the mask
            new_setting_values = setting_values
            new_setting_values.insert(6, 'No')
            setting_values = new_setting_values
            variable_revision_number = 3
        if (not from_matlab) and variable_revision_number == 3:
            # Log transform -> legacy log transform
            if setting_values[0] == O_LOG_TRANSFORM:
                setting_values = [O_LOG_TRANSFORM_LEGACY] + setting_values[1:]
            variable_revision_number = 4
        return setting_values, variable_revision_number, from_matlab