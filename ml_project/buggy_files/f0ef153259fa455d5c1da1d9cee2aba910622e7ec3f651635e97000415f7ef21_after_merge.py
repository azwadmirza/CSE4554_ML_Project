    def _compile_builder(self, append_unknown=True):
        defaults = self.defaults or {}
        dom_ops = []
        url_ops = []

        opl = dom_ops
        for is_dynamic, data in self._trace:
            if data == "|" and opl is dom_ops:
                opl = url_ops
                continue
            # this seems like a silly case to ever come up but:
            # if a default is given for a value that appears in the rule,
            # resolve it to a constant ahead of time
            if is_dynamic and data in defaults:
                data = self._converters[data].to_url(defaults[data])
                opl.append((False, data))
            elif not is_dynamic:
                opl.append(
                    (False, url_quote(to_bytes(data, self.map.charset), safe="/:|+"))
                )
            else:
                opl.append((True, data))

        def _convert(elem):
            ret = _prefix_names(_CALL_CONVERTER_CODE_FMT.format(elem=elem))
            ret.args = [ast.Name(str(elem), ast.Load())]  # str for py2
            return ret

        def _parts(ops):
            parts = [
                _convert(elem) if is_dynamic else ast.Str(s=elem)
                for is_dynamic, elem in ops
            ]
            parts = parts or [ast.Str("")]
            # constant fold
            ret = [parts[0]]
            for p in parts[1:]:
                if isinstance(p, ast.Str) and isinstance(ret[-1], ast.Str):
                    ret[-1] = ast.Str(ret[-1].s + p.s)
                else:
                    ret.append(p)
            return ret

        dom_parts = _parts(dom_ops)
        url_parts = _parts(url_ops)
        if not append_unknown:
            body = []
        else:
            body = [_IF_KWARGS_URL_ENCODE_AST]
            url_parts.extend(_URL_ENCODE_AST_NAMES)

        def _join(parts):
            if len(parts) == 1:  # shortcut
                return parts[0]
            elif hasattr(ast, "JoinedStr"):  # py36+
                return ast.JoinedStr(parts)
            else:
                call = _prefix_names('"".join()')
                call.args = [ast.Tuple(parts, ast.Load())]
                return call

        body.append(
            ast.Return(ast.Tuple([_join(dom_parts), _join(url_parts)], ast.Load()))
        )

        # str is necessary for python2
        pargs = [
            str(elem)
            for is_dynamic, elem in dom_ops + url_ops
            if is_dynamic and elem not in defaults
        ]
        kargs = [str(k) for k in defaults]

        func_ast = _prefix_names("def _(): pass")
        func_ast.name = "<builder:{!r}>".format(self.rule)
        if hasattr(ast, "arg"):  # py3
            func_ast.args.args.append(ast.arg(".self", None))
            for arg in pargs + kargs:
                func_ast.args.args.append(ast.arg(arg, None))
            func_ast.args.kwarg = ast.arg(".kwargs", None)
        else:
            func_ast.args.args.append(ast.Name(".self", ast.Load()))
            for arg in pargs + kargs:
                func_ast.args.args.append(ast.Name(arg, ast.Load()))
            func_ast.args.kwarg = ".kwargs"
        for _ in kargs:
            func_ast.args.defaults.append(ast.Str(""))
        func_ast.body = body

        module = ast.fix_missing_locations(ast.Module([func_ast]))
        code = compile(module, "<werkzeug routing>", "exec")
        return self._get_func_code(code, func_ast.name)