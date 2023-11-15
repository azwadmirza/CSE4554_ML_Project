    def handle(self, line_info):
        """Handle lines which can be auto-executed, quoting if requested."""
        line    = line_info.line
        ifun    = line_info.ifun
        the_rest = line_info.the_rest
        pre     = line_info.pre
        esc     = line_info.esc
        continue_prompt = line_info.continue_prompt
        obj = line_info.ofind(self)['obj']
        #print 'pre <%s> ifun <%s> rest <%s>' % (pre,ifun,the_rest)  # dbg

        # This should only be active for single-line input!
        if continue_prompt:
            return line

        force_auto = isinstance(obj, IPyAutocall)

        # User objects sometimes raise exceptions on attribute access other
        # than AttributeError (we've seen it in the past), so it's safest to be
        # ultra-conservative here and catch all.
        try:
            auto_rewrite = obj.rewrite
        except Exception:
            auto_rewrite = True

        if esc == ESC_QUOTE:
            # Auto-quote splitting on whitespace
            newcmd = '%s("%s")' % (ifun,'", "'.join(the_rest.split()) )
        elif esc == ESC_QUOTE2:
            # Auto-quote whole string
            newcmd = '%s("%s")' % (ifun,the_rest)
        elif esc == ESC_PAREN:
            newcmd = '%s(%s)' % (ifun,",".join(the_rest.split()))
        else:
            # Auto-paren.
            # We only apply it to argument-less calls if the autocall
            # parameter is set to 2.  We only need to check that autocall is <
            # 2, since this function isn't called unless it's at least 1.
            if not the_rest and (self.shell.autocall < 2) and not force_auto:
                newcmd = '%s %s' % (ifun,the_rest)
                auto_rewrite = False
            else:
                if not force_auto and the_rest.startswith('['):
                    if hasattr(obj,'__getitem__'):
                        # Don't autocall in this case: item access for an object
                        # which is BOTH callable and implements __getitem__.
                        newcmd = '%s %s' % (ifun,the_rest)
                        auto_rewrite = False
                    else:
                        # if the object doesn't support [] access, go ahead and
                        # autocall
                        newcmd = '%s(%s)' % (ifun.rstrip(),the_rest)
                elif the_rest.endswith(';'):
                    newcmd = '%s(%s);' % (ifun.rstrip(),the_rest[:-1])
                else:
                    newcmd = '%s(%s)' % (ifun.rstrip(), the_rest)

        if auto_rewrite:
            self.shell.auto_rewrite_input(newcmd)

        return newcmd