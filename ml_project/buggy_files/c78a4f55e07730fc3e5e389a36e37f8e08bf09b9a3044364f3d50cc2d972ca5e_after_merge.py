    def commit(self):
        matching_output = self.data
        non_matching_output = None
        annotated_output = None

        self.Error.clear()
        if self.data:
            domain = self.data.domain
            conditions = []
            for attr_name, oper_idx, values in self.conditions:
                if attr_name in self.AllTypes:
                    attr_index = attr = None
                    attr_type = self.AllTypes[attr_name]
                    operators = self.Operators[attr_name]
                else:
                    attr_index = domain.index(attr_name)
                    attr = domain[attr_index]
                    attr_type = vartype(attr)
                    operators = self.Operators[type(attr)]
                opertype, _ = operators[oper_idx]
                if attr_type == 0:
                    filter = data_filter.IsDefined()
                elif attr_type in (2, 4):  # continuous, time
                    try:
                        floats = self._values_to_floats(attr, values)
                    except ValueError as e:
                        self.Error.parsing_error(e.args[0])
                        return
                    if floats is None:
                        continue
                    filter = data_filter.FilterContinuous(
                        attr_index, opertype, *floats)
                elif attr_type == 3:  # string
                    filter = data_filter.FilterString(
                        attr_index, opertype, *[str(v) for v in values])
                else:
                    if opertype == FilterDiscreteType.IsDefined:
                        f_values = None
                    else:
                        if not values or not values[0]:
                            continue
                        values = [attr.values[i-1] for i in values]
                        if opertype == FilterDiscreteType.Equal:
                            f_values = {values[0]}
                        elif opertype == FilterDiscreteType.NotEqual:
                            f_values = set(attr.values)
                            f_values.remove(values[0])
                        elif opertype == FilterDiscreteType.In:
                            f_values = set(values)
                        else:
                            raise ValueError("invalid operand")
                    filter = data_filter.FilterDiscrete(attr_index, f_values)
                conditions.append(filter)

            if conditions:
                self.filters = data_filter.Values(conditions)
                matching_output = self.filters(self.data)
                self.filters.negate = True
                non_matching_output = self.filters(self.data)

                row_sel = np.in1d(self.data.ids, matching_output.ids)
                annotated_output = create_annotated_table(self.data, row_sel)

            # if hasattr(self.data, "name"):
            #     matching_output.name = self.data.name
            #     non_matching_output.name = self.data.name

            purge_attrs = self.purge_attributes
            purge_classes = self.purge_classes
            if (purge_attrs or purge_classes) and \
                    not isinstance(self.data, SqlTable):
                attr_flags = sum([Remove.RemoveConstant * purge_attrs,
                                  Remove.RemoveUnusedValues * purge_attrs])
                class_flags = sum([Remove.RemoveConstant * purge_classes,
                                   Remove.RemoveUnusedValues * purge_classes])
                # same settings used for attributes and meta features
                remover = Remove(attr_flags, class_flags, attr_flags)

                matching_output = remover(matching_output)
                non_matching_output = remover(non_matching_output)
                annotated_output = remover(annotated_output)

        if matching_output is not None and not len(matching_output):
            matching_output = None
        if non_matching_output is not None and not len(non_matching_output):
            non_matching_output = None
        if annotated_output is not None and not len(annotated_output):
            annotated_output = None

        self.Outputs.matching_data.send(matching_output)
        self.Outputs.unmatched_data.send(non_matching_output)
        self.Outputs.annotated_data.send(annotated_output)

        self.match_desc = report.describe_data_brief(matching_output)
        self.nonmatch_desc = report.describe_data_brief(non_matching_output)

        self.update_info(matching_output, self.data_out_rows, "Out: ")