        def check_var(name):
            tv = self.typevars[name]
            if not tv.defined:
                offender = find_offender(name)
                val = getattr(offender, 'value', 'unknown operation')
                loc = getattr(offender, 'loc', 'unknown location')
                msg = "Undefined variable '%s', operation: %s, location: %s"
                raise TypingError(msg % (var, val, loc), loc)
            tp = tv.getone()
            if not tp.is_precise():
                offender = find_offender(name, exhaustive=True)
                msg = ("Cannot infer the type of variable '%s'%s, "
                      "have imprecise type: %s. %s")
                istmp = " (temporary variable)" if var.startswith('$') else ""
                loc = getattr(offender, 'loc', 'unknown location')
                # is this an untyped list? try and provide help
                extra_msg = diagnose_imprecision(offender)
                raise TypingError(msg % (var, istmp, tp, extra_msg), loc)
            else: # type is precise, hold it
                typdict[var] = tp