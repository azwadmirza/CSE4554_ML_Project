    def p_subproc_arg_part(self, p):
        """subproc_arg_part : NAME
                            | TILDE
                            | PERIOD
                            | DIVIDE
                            | MINUS
                            | PLUS
                            | COLON
                            | AT
                            | ATDOLLAR
                            | EQUALS
                            | TIMES
                            | POW
                            | MOD
                            | XOR
                            | DOUBLEDIV
                            | ELLIPSIS
                            | NONE
                            | TRUE
                            | FALSE
                            | NUMBER
                            | STRING
                            | COMMA
                            | QUESTION
                            | DOLLAR_NAME
        """
        # Many tokens cannot be part of this list, such as $, ', ", ()
        # Use a string atom instead.
        p[0] = p[1]