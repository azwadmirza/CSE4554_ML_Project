    def _calculate_binary_op(self, f, other, inplace=False, drop_na_vars=True):

        def apply_over_both(lhs_data_vars, rhs_data_vars, lhs_vars, rhs_vars):
            dest_vars = OrderedDict()
            performed_op = False
            for k in lhs_data_vars:
                if k in rhs_data_vars:
                    dest_vars[k] = f(lhs_vars[k], rhs_vars[k])
                    performed_op = True
                elif inplace:
                    raise ValueError(
                        'datasets must have the same data variables '
                        'for in-place arithmetic operations: %s, %s'
                        % (list(lhs_data_vars), list(rhs_data_vars)))
                elif not drop_na_vars:
                    # this shortcuts left alignment of variables for fillna
                    dest_vars[k] = lhs_vars[k]
            if not performed_op:
                raise ValueError(
                    'datasets have no overlapping data variables: %s, %s'
                    % (list(lhs_data_vars), list(rhs_data_vars)))
            return dest_vars

        if utils.is_dict_like(other) and not isinstance(other, Dataset):
            # can't use our shortcut of doing the binary operation with
            # Variable objects, so apply over our data vars instead.
            new_data_vars = apply_over_both(self.data_vars, other,
                                            self.data_vars, other)
            return Dataset(new_data_vars)

        other_coords = getattr(other, 'coords', None)
        ds = self.coords.merge(other_coords)

        if isinstance(other, Dataset):
            new_vars = apply_over_both(self.data_vars, other.data_vars,
                                       self.variables, other.variables)
        else:
            other_variable = getattr(other, 'variable', other)
            new_vars = OrderedDict((k, f(self.variables[k], other_variable))
                                   for k in self.data_vars)

        ds._variables.update(new_vars)
        return ds