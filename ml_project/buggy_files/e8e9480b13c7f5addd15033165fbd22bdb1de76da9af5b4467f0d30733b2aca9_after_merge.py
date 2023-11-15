    def _compile_assign(self, name, result,
                        start_line, start_column):

        str_name = "%s" % name
        if _is_hy_builtin(str_name, self.module_name):
            raise HyTypeError(name,
                              "Can't assign to a builtin: `%s'" % str_name)

        result = self.compile(result)
        ld_name = self.compile(name)

        if isinstance(ld_name.expr, ast.Call):
            raise HyTypeError(name,
                              "Can't assign to a callable: `%s'" % str_name)

        if result.temp_variables \
           and isinstance(name, HyString) \
           and '.' not in name:
            result.rename(name)
        else:
            st_name = self._storeize(ld_name)
            result += ast.Assign(
                lineno=start_line,
                col_offset=start_column,
                targets=[st_name],
                value=result.force_expr)

        result += ld_name
        return result