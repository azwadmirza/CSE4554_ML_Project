    def p_subproc_arg_part(self, p):
        # Many tokens cannot be part of this rule, such as $, ', ", ()
        # Use a string atom instead. See above attachment functions
        p[0] = p[1]