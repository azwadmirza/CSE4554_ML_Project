    def __init__(self,
                 lexer_optimize=True,
                 lexer_table='xonsh.lexer_table',
                 yacc_optimize=True,
                 yacc_table='xonsh.parser_table',
                 yacc_debug=False,
                 outputdir=None):
        """Parameters
        ----------
        lexer_optimize : bool, optional
            Set to false when unstable and true when lexer is stable.
        lexer_table : str, optional
            Lexer module used when optimized.
        yacc_optimize : bool, optional
            Set to false when unstable and true when parser is stable.
        yacc_table : str, optional
            Parser module used when optimized.
        yacc_debug : debug, optional
            Dumps extra debug info.
        outputdir : str or None, optional
            The directory to place generated tables within. Defaults to the root
            xonsh dir.
        """
        self.lexer = lexer = Lexer()
        self.tokens = lexer.tokens

        self._lines = None
        self.xonsh_code = None
        self._attach_nocomma_tok_rules()
        self._attach_nocloser_base_rules()
        self._attach_nodedent_base_rules()
        self._attach_nonewline_base_rules()
        self._attach_subproc_arg_part_rules()

        opt_rules = [
            'newlines', 'arglist', 'func_call', 'rarrow_test', 'typedargslist',
            'equals_test', 'colon_test', 'tfpdef', 'comma_tfpdef_list',
            'comma_pow_tfpdef', 'vfpdef', 'comma_vfpdef_list',
            'comma_pow_vfpdef', 'equals_yield_expr_or_testlist_list',
            'testlist', 'as_name', 'period_or_ellipsis_list',
            'comma_import_as_name_list', 'comma_dotted_as_name_list',
            'comma_name_list', 'comma_test', 'elif_part_list', 'finally_part',
            'varargslist', 'or_and_test_list', 'and_not_test_list',
            'comp_op_expr_list', 'xor_and_expr_list',
            'ampersand_shift_expr_list', 'shift_arith_expr_list',
            'op_factor_list', 'trailer_list', 'testlist_comp',
            'yield_expr_or_testlist_comp', 'dictorsetmaker',
            'comma_subscript_list', 'test', 'sliceop', 'comp_iter',
            'yield_arg', 'test_comma_list',
            'macroarglist', 'any_raw_toks']
        for rule in opt_rules:
            self._opt_rule(rule)

        list_rules = [
            'comma_tfpdef', 'comma_vfpdef', 'semi_small_stmt',
            'comma_test_or_star_expr', 'period_or_ellipsis',
            'comma_import_as_name', 'comma_dotted_as_name', 'period_name',
            'comma_name', 'elif_part', 'except_part', 'comma_with_item',
            'or_and_test', 'and_not_test', 'comp_op_expr', 'pipe_xor_expr',
            'xor_and_expr', 'ampersand_shift_expr', 'shift_arith_expr',
            'pm_term', 'op_factor', 'trailer', 'comma_subscript',
            'comma_expr_or_star_expr', 'comma_test', 'comma_argument',
            'comma_item', 'attr_period_name', 'test_comma',
            'equals_yield_expr_or_testlist', 'comma_nocomma']
        for rule in list_rules:
            self._list_rule(rule)

        tok_rules = ['def', 'class', 'return', 'number', 'name', 'bang',
                     'none', 'true', 'false', 'ellipsis', 'if', 'del',
                     'assert', 'lparen', 'lbrace', 'lbracket', 'string',
                     'times', 'plus', 'minus', 'divide', 'doublediv', 'mod',
                     'at', 'lshift', 'rshift', 'pipe', 'xor', 'ampersand',
                     'for', 'colon', 'import', 'except', 'nonlocal', 'global',
                     'yield', 'from', 'raise', 'with', 'dollar_lparen',
                     'dollar_lbrace', 'dollar_lbracket', 'try',
                     'bang_lparen', 'bang_lbracket', 'comma', 'rparen',
                     'rbracket', 'at_lparen', 'atdollar_lparen', 'indent',
                     'dedent', 'newline']
        for rule in tok_rules:
            self._tok_rule(rule)

        yacc_kwargs = dict(module=self,
                           debug=yacc_debug,
                           start='start_symbols',
                           optimize=yacc_optimize,
                           tabmodule=yacc_table)
        if not yacc_debug:
            yacc_kwargs['errorlog'] = yacc.NullLogger()
        if outputdir is None:
            outputdir = os.path.dirname(os.path.dirname(__file__))
        yacc_kwargs['outputdir'] = outputdir
        if yacc_debug:
            # create parser on main thread
            self.parser = yacc.yacc(**yacc_kwargs)
        else:
            self.parser = None
            YaccLoader(self, yacc_kwargs)

        # Keeps track of the last token given to yacc (the lookahead token)
        self._last_yielded_token = None