    def format_record(self, frame, file, lnum, func, lines, index):
        """Format a single stack frame"""
        Colors = self.Colors  # just a shorthand + quicker name lookup
        ColorsNormal = Colors.Normal  # used a lot
        col_scheme = self.color_scheme_table.active_scheme_name
        indent = ' ' * INDENT_SIZE
        em_normal = '%s\n%s%s' % (Colors.valEm, indent, ColorsNormal)
        undefined = '%sundefined%s' % (Colors.em, ColorsNormal)
        tpl_link = '%s%%s%s' % (Colors.filenameEm, ColorsNormal)
        tpl_call = 'in %s%%s%s%%s%s' % (Colors.vName, Colors.valEm,
                                        ColorsNormal)
        tpl_call_fail = 'in %s%%s%s(***failed resolving arguments***)%s' % \
                        (Colors.vName, Colors.valEm, ColorsNormal)
        tpl_local_var = '%s%%s%s' % (Colors.vName, ColorsNormal)
        tpl_global_var = '%sglobal%s %s%%s%s' % (Colors.em, ColorsNormal,
                                                 Colors.vName, ColorsNormal)
        tpl_name_val = '%%s %s= %%s%s' % (Colors.valEm, ColorsNormal)

        tpl_line = '%s%%s%s %%s' % (Colors.lineno, ColorsNormal)
        tpl_line_em = '%s%%s%s %%s%s' % (Colors.linenoEm, Colors.line,
                                         ColorsNormal)

        abspath = os.path.abspath


        if not file:
            file = '?'
        elif file.startswith(str("<")) and file.endswith(str(">")):
            # Not a real filename, no problem...
            pass
        elif not os.path.isabs(file):
            # Try to make the filename absolute by trying all
            # sys.path entries (which is also what linecache does)
            for dirname in sys.path:
                try:
                    fullname = os.path.join(dirname, file)
                    if os.path.isfile(fullname):
                        file = os.path.abspath(fullname)
                        break
                except Exception:
                    # Just in case that sys.path contains very
                    # strange entries...
                    pass

        file = py3compat.cast_unicode(file, util_path.fs_encoding)
        link = tpl_link % util_path.compress_user(file)
        args, varargs, varkw, locals = inspect.getargvalues(frame)

        if func == '?':
            call = ''
        else:
            # Decide whether to include variable details or not
            var_repr = self.include_vars and eqrepr or nullrepr
            try:
                call = tpl_call % (func, inspect.formatargvalues(args,
                                                                 varargs, varkw,
                                                                 locals, formatvalue=var_repr))
            except KeyError:
                # This happens in situations like errors inside generator
                # expressions, where local variables are listed in the
                # line, but can't be extracted from the frame.  I'm not
                # 100% sure this isn't actually a bug in inspect itself,
                # but since there's no info for us to compute with, the
                # best we can do is report the failure and move on.  Here
                # we must *not* call any traceback construction again,
                # because that would mess up use of %debug later on.  So we
                # simply report the failure and move on.  The only
                # limitation will be that this frame won't have locals
                # listed in the call signature.  Quite subtle problem...
                # I can't think of a good way to validate this in a unit
                # test, but running a script consisting of:
                #  dict( (k,v.strip()) for (k,v) in range(10) )
                # will illustrate the error, if this exception catch is
                # disabled.
                call = tpl_call_fail % func

        # Don't attempt to tokenize binary files.
        if file.endswith(('.so', '.pyd', '.dll')):
            return '%s %s\n' % (link, call)

        elif file.endswith(('.pyc', '.pyo')):
            # Look up the corresponding source file.
            try:
                file = openpy.source_from_cache(file)
            except ValueError:
                # Failed to get the source file for some reason
                # E.g. https://github.com/ipython/ipython/issues/9486
                return '%s %s\n' % (link, call)

        def linereader(file=file, lnum=[lnum], getline=linecache.getline):
            line = getline(file, lnum[0])
            lnum[0] += 1
            return line

        # Build the list of names on this line of code where the exception
        # occurred.
        try:
            names = []
            name_cont = False

            for token_type, token, start, end, line in generate_tokens(linereader):
                # build composite names
                if token_type == tokenize.NAME and token not in keyword.kwlist:
                    if name_cont:
                        # Continuation of a dotted name
                        try:
                            names[-1].append(token)
                        except IndexError:
                            names.append([token])
                        name_cont = False
                    else:
                        # Regular new names.  We append everything, the caller
                        # will be responsible for pruning the list later.  It's
                        # very tricky to try to prune as we go, b/c composite
                        # names can fool us.  The pruning at the end is easy
                        # to do (or the caller can print a list with repeated
                        # names if so desired.
                        names.append([token])
                elif token == '.':
                    name_cont = True
                elif token_type == tokenize.NEWLINE:
                    break

        except (IndexError, UnicodeDecodeError, SyntaxError):
            # signals exit of tokenizer
            # SyntaxError can occur if the file is not actually Python
            #  - see gh-6300
            pass
        except tokenize.TokenError as msg:
            _m = ("An unexpected error occurred while tokenizing input\n"
                  "The following traceback may be corrupted or invalid\n"
                  "The error message is: %s\n" % msg)
            error(_m)

        # Join composite names (e.g. "dict.fromkeys")
        names = ['.'.join(n) for n in names]
        # prune names list of duplicates, but keep the right order
        unique_names = uniq_stable(names)

        # Start loop over vars
        lvals = []
        if self.include_vars:
            for name_full in unique_names:
                name_base = name_full.split('.', 1)[0]
                if name_base in frame.f_code.co_varnames:
                    if name_base in locals:
                        try:
                            value = repr(eval(name_full, locals))
                        except:
                            value = undefined
                    else:
                        value = undefined
                    name = tpl_local_var % name_full
                else:
                    if name_base in frame.f_globals:
                        try:
                            value = repr(eval(name_full, frame.f_globals))
                        except:
                            value = undefined
                    else:
                        value = undefined
                    name = tpl_global_var % name_full
                lvals.append(tpl_name_val % (name, value))
        if lvals:
            lvals = '%s%s' % (indent, em_normal.join(lvals))
        else:
            lvals = ''

        level = '%s %s\n' % (link, call)

        if index is None:
            return level
        else:
            _line_format = PyColorize.Parser(style=col_scheme, parent=self).format2
            return '%s%s' % (level, ''.join(
                _format_traceback_lines(lnum, index, lines, Colors, lvals,
                                         _line_format)))