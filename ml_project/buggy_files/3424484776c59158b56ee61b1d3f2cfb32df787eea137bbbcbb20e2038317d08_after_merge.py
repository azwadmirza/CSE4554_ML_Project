def _fix_py3_plus(contents_text):  # type: (str) -> str
    try:
        ast_obj = ast_parse(contents_text)
    except SyntaxError:
        return contents_text

    visitor = FindPy3Plus()
    visitor.visit(ast_obj)

    if not any((
            visitor.bases_to_remove,
            visitor.encode_calls,
            visitor.if_py2_blocks_else,
            visitor.if_py3_blocks,
            visitor.if_py3_blocks_else,
            visitor.native_literals,
            visitor.io_open_calls,
            visitor.os_error_alias_calls,
            visitor.os_error_alias_simple,
            visitor.os_error_alias_excepts,
            visitor.six_add_metaclass,
            visitor.six_b,
            visitor.six_calls,
            visitor.six_iter,
            visitor.six_raise_from,
            visitor.six_reraise,
            visitor.six_remove_decorators,
            visitor.six_simple,
            visitor.six_type_ctx,
            visitor.six_with_metaclass,
            visitor.super_calls,
            visitor.yield_from_fors,
    )):
        return contents_text

    try:
        tokens = src_to_tokens(contents_text)
    except tokenize.TokenError:  # pragma: no cover (bpo-2180)
        return contents_text

    _fixup_dedent_tokens(tokens)

    def _replace(i, mapping, node):
        # type: (int, Dict[str, str], NameOrAttr) -> None
        new_token = Token('CODE', _get_tmpl(mapping, node))
        if isinstance(node, ast.Name):
            tokens[i] = new_token
        else:
            j = i
            while tokens[j].src != node.attr:
                # timid: if we see a parenthesis here, skip it
                if tokens[j].src == ')':
                    return
                j += 1
            tokens[i:j + 1] = [new_token]

    for i, token in reversed_enumerate(tokens):
        if not token.src:
            continue
        elif token.offset in visitor.bases_to_remove:
            _remove_base_class(tokens, i)
        elif token.offset in visitor.if_py3_blocks:
            if tokens[i].src == 'if':
                if_block = Block.find(tokens, i)
                if_block.dedent(tokens)
                del tokens[if_block.start:if_block.block]
            else:
                if_block = Block.find(tokens, _find_elif(tokens, i))
                if_block.replace_condition(tokens, [Token('NAME', 'else')])
        elif token.offset in visitor.if_py2_blocks_else:
            if tokens[i].src == 'if':
                if_block, else_block = _find_if_else_block(tokens, i)
                else_block.dedent(tokens)
                del tokens[if_block.start:else_block.block]
            else:
                j = _find_elif(tokens, i)
                if_block, else_block = _find_if_else_block(tokens, j)
                del tokens[if_block.start:else_block.start]
        elif token.offset in visitor.if_py3_blocks_else:
            if tokens[i].src == 'if':
                if_block, else_block = _find_if_else_block(tokens, i)
                if_block.dedent(tokens)
                del tokens[if_block.end:else_block.end]
                del tokens[if_block.start:if_block.block]
            else:
                j = _find_elif(tokens, i)
                if_block, else_block = _find_if_else_block(tokens, j)
                del tokens[if_block.end:else_block.end]
                if_block.replace_condition(tokens, [Token('NAME', 'else')])
        elif token.offset in visitor.six_type_ctx:
            _replace(i, SIX_TYPE_CTX_ATTRS, visitor.six_type_ctx[token.offset])
        elif token.offset in visitor.six_simple:
            _replace(i, SIX_SIMPLE_ATTRS, visitor.six_simple[token.offset])
        elif token.offset in visitor.six_remove_decorators:
            _remove_decorator(tokens, i)
        elif token.offset in visitor.six_b:
            j = _find_open_paren(tokens, i)
            if (
                    tokens[j + 1].name == 'STRING' and
                    _is_ascii(tokens[j + 1].src) and
                    tokens[j + 2].src == ')'
            ):
                func_args, end = _parse_call_args(tokens, j)
                _replace_call(tokens, i, end, func_args, SIX_B_TMPL)
        elif token.offset in visitor.six_iter:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            call = visitor.six_iter[token.offset]
            assert isinstance(call.func, (ast.Name, ast.Attribute))
            template = 'iter({})'.format(_get_tmpl(SIX_CALLS, call.func))
            _replace_call(tokens, i, end, func_args, template)
        elif token.offset in visitor.six_calls:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            call = visitor.six_calls[token.offset]
            assert isinstance(call.func, (ast.Name, ast.Attribute))
            template = _get_tmpl(SIX_CALLS, call.func)
            _replace_call(tokens, i, end, func_args, template)
        elif token.offset in visitor.six_raise_from:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            _replace_call(tokens, i, end, func_args, RAISE_FROM_TMPL)
        elif token.offset in visitor.six_reraise:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            if len(func_args) == 2:
                _replace_call(tokens, i, end, func_args, RERAISE_2_TMPL)
            else:
                _replace_call(tokens, i, end, func_args, RERAISE_3_TMPL)
        elif token.offset in visitor.six_add_metaclass:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            metaclass = 'metaclass={}'.format(_arg_str(tokens, *func_args[0]))
            # insert `metaclass={args[0]}` into `class:`
            # search forward for the `class` token
            j = i + 1
            while tokens[j].src != 'class':
                j += 1
            class_token = j
            # then search forward for a `:` token, not inside a brace
            j = _find_block_start(tokens, j)
            last_paren = -1
            for k in range(class_token, j):
                if tokens[k].src == ')':
                    last_paren = k

            if last_paren == -1:
                tokens.insert(j, Token('CODE', '({})'.format(metaclass)))
            else:
                insert = last_paren - 1
                while tokens[insert].name in NON_CODING_TOKENS:
                    insert -= 1
                if tokens[insert].src == '(':  # no bases
                    src = metaclass
                elif tokens[insert].src != ',':
                    src = ', {}'.format(metaclass)
                else:
                    src = ' {},'.format(metaclass)
                tokens.insert(insert + 1, Token('CODE', src))
            _remove_decorator(tokens, i)
        elif token.offset in visitor.six_with_metaclass:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            if len(func_args) == 1:
                tmpl = WITH_METACLASS_NO_BASES_TMPL
            else:
                tmpl = WITH_METACLASS_BASES_TMPL
            _replace_call(tokens, i, end, func_args, tmpl)
        elif token.offset in visitor.super_calls:
            i = _find_open_paren(tokens, i)
            call = visitor.super_calls[token.offset]
            victims = _victims(tokens, i, call, gen=False)
            del tokens[victims.starts[0] + 1:victims.ends[-1]]
        elif token.offset in visitor.encode_calls:
            i = _find_open_paren(tokens, i)
            call = visitor.encode_calls[token.offset]
            victims = _victims(tokens, i, call, gen=False)
            del tokens[victims.starts[0] + 1:victims.ends[-1]]
        elif token.offset in visitor.native_literals:
            j = _find_open_paren(tokens, i)
            func_args, end = _parse_call_args(tokens, j)
            if any(tok.name == 'NL' for tok in tokens[i:end]):
                continue
            if func_args:
                _replace_call(tokens, i, end, func_args, '{args[0]}')
            else:
                tokens[i:end] = [token._replace(name='STRING', src="''")]
        elif token.offset in visitor.io_open_calls:
            j = _find_open_paren(tokens, i)
            tokens[i:j] = [token._replace(name='NAME', src='open')]
        elif token.offset in visitor.os_error_alias_calls:
            j = _find_open_paren(tokens, i)
            tokens[i:j] = [token._replace(name='NAME', src='OSError')]
        elif token.offset in visitor.os_error_alias_simple:
            node = visitor.os_error_alias_simple[token.offset]
            _replace(i, collections.defaultdict(lambda: 'OSError'), node)
        elif token.offset in visitor.os_error_alias_excepts:
            line, utf8_byte_offset = token.line, token.utf8_byte_offset

            # find all the arg strs in the tuple
            except_index = i
            while tokens[except_index].src != 'except':
                except_index -= 1
            start = _find_open_paren(tokens, except_index)
            func_args, end = _parse_call_args(tokens, start)

            # save the exceptions and remove the block
            arg_strs = [_arg_str(tokens, *arg) for arg in func_args]
            del tokens[start:end]

            # rewrite the block without dupes
            args = []
            for arg in arg_strs:
                left, part, right = arg.partition('.')
                if (
                        left in visitor.OS_ERROR_ALIAS_MODULES and
                        part == '.' and
                        right == 'error'
                ):
                    args.append('OSError')
                elif (
                        left in visitor.OS_ERROR_ALIASES and
                        part == right == ''
                ):
                    args.append('OSError')
                elif (
                        left == 'error' and
                        part == right == '' and
                        (
                            'error' in visitor.from_imported_names['mmap'] or
                            'error' in visitor.from_imported_names['select'] or
                            'error' in visitor.from_imported_names['socket']
                        )
                ):
                    args.append('OSError')
                else:
                    args.append(arg)

            unique_args = tuple(collections.OrderedDict.fromkeys(args))

            if len(unique_args) > 1:
                joined = '({})'.format(', '.join(unique_args))
            elif tokens[start - 1].name != 'UNIMPORTANT_WS':
                joined = ' {}'.format(unique_args[0])
            else:
                joined = unique_args[0]

            new = Token('CODE', joined, line, utf8_byte_offset)
            tokens.insert(start, new)

            visitor.os_error_alias_excepts.pop(token.offset)
        elif token.offset in visitor.yield_from_fors:
            _replace_yield(tokens, i)

    return tokens_to_src(tokens)