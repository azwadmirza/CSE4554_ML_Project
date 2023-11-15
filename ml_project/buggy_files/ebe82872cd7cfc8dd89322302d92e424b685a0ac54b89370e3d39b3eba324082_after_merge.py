    def conditional_write(self, line, stmt, variables, conditional_write_vars,
                          created_vars):
        if stmt.var in conditional_write_vars:
            subs = {}
            index = conditional_write_vars[stmt.var]
            # we replace all var with var[index], but actually we use this repl_string first because
            # we don't want to end up with lines like x[not_refractory[not_refractory]] when
            # multiple substitution passes are invoked
            repl_string = '#$(@#&$@$*U#@)$@(#'  # this string shouldn't occur anywhere I hope! :)
            for varname, var in variables.items():
                if isinstance(var, ArrayVariable) and not var.scalar:
                    subs[varname] = varname + '[' + repl_string + ']'
            # all newly created vars are arrays and will need indexing
            for varname in created_vars:
                subs[varname] = varname + '[' + repl_string + ']'
            # Also index _vectorisation_idx so that e.g. rand() works correctly
            subs['_vectorisation_idx'] = '_vectorisation_idx' + '[' + repl_string + ']'

            line = word_substitute(line, subs)
            line = line.replace(repl_string, index)
        return line