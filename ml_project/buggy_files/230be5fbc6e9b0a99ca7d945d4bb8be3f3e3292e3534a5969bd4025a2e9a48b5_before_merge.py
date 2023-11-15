    def generate_stararg_copy_code(self, code):
        if not self.star_arg:
            code.globalstate.use_utility_code(
                UtilityCode.load_cached("RaiseArgTupleInvalid", "FunctionArguments.c"))
            code.putln("if (unlikely(%s > 0)) {" % Naming.nargs_cname)
            code.put('__Pyx_RaiseArgtupleInvalid("%s", 1, 0, 0, %s); return %s;' % (
                self.name, Naming.nargs_cname, self.error_value()))
            code.putln("}")

        if self.starstar_arg:
            if self.star_arg or not self.starstar_arg.entry.cf_used:
                kwarg_check = "unlikely(%s)" % Naming.kwds_cname
            else:
                kwarg_check = "%s" % Naming.kwds_cname
        else:
            kwarg_check = "unlikely(%s) && __Pyx_NumKwargs_%s(%s)" % (
                Naming.kwds_cname, self.signature.fastvar, Naming.kwds_cname)
        code.globalstate.use_utility_code(
            UtilityCode.load_cached("KeywordStringCheck", "FunctionArguments.c"))
        code.putln(
            "if (%s && unlikely(!__Pyx_CheckKeywordStrings(%s, \"%s\", %d))) return %s;" % (
                kwarg_check, Naming.kwds_cname, self.name,
                bool(self.starstar_arg), self.error_value()))

        if self.starstar_arg and self.starstar_arg.entry.cf_used:
            code.putln("if (%s) {" % kwarg_check)
            code.putln("%s = __Pyx_KwargsAsDict_%s(%s, %s);" % (
                self.starstar_arg.entry.cname,
                self.signature.fastvar,
                Naming.kwds_cname,
                Naming.kwvalues_cname))
            code.putln("if (unlikely(!%s)) return %s;" % (
                self.starstar_arg.entry.cname, self.error_value()))
            code.put_gotref(self.starstar_arg.entry.cname, py_object_type)
            code.putln("} else {")
            allow_null = all(ref.node.allow_null for ref in self.starstar_arg.entry.cf_references)
            if allow_null:
                code.putln("%s = NULL;" % (self.starstar_arg.entry.cname,))
            else:
                code.putln("%s = PyDict_New();" % (self.starstar_arg.entry.cname,))
                code.putln("if (unlikely(!%s)) return %s;" % (
                    self.starstar_arg.entry.cname, self.error_value()))
                code.put_var_gotref(self.starstar_arg.entry)
            self.starstar_arg.entry.xdecref_cleanup = allow_null
            code.putln("}")

        if self.self_in_stararg and not self.target.is_staticmethod:
            assert not self.signature.use_fastcall
            # need to create a new tuple with 'self' inserted as first item
            code.put("%s = PyTuple_New(%s + 1); if (unlikely(!%s)) " % (
                self.star_arg.entry.cname,
                Naming.nargs_cname,
                self.star_arg.entry.cname))
            if self.starstar_arg and self.starstar_arg.entry.cf_used:
                code.putln("{")
                code.put_var_xdecref_clear(self.starstar_arg.entry)
                code.putln("return %s;" % self.error_value())
                code.putln("}")
            else:
                code.putln("return %s;" % self.error_value())
            code.put_var_gotref(self.star_arg.entry)
            code.put_incref(Naming.self_cname, py_object_type)
            code.put_giveref(Naming.self_cname, py_object_type)
            code.putln("PyTuple_SET_ITEM(%s, 0, %s);" % (
                self.star_arg.entry.cname, Naming.self_cname))
            temp = code.funcstate.allocate_temp(PyrexTypes.c_py_ssize_t_type, manage_ref=False)
            code.putln("for (%s=0; %s < %s; %s++) {" % (
                temp, temp, Naming.nargs_cname, temp))
            code.putln("PyObject* item = PyTuple_GET_ITEM(%s, %s);" % (
                Naming.args_cname, temp))
            code.put_incref("item", py_object_type)
            code.put_giveref("item", py_object_type)
            code.putln("PyTuple_SET_ITEM(%s, %s+1, item);" % (
                self.star_arg.entry.cname, temp))
            code.putln("}")
            code.funcstate.release_temp(temp)
            self.star_arg.entry.xdecref_cleanup = 0
        elif self.star_arg:
            assert not self.signature.use_fastcall
            code.put_incref(Naming.args_cname, py_object_type)
            code.putln("%s = %s;" % (
                self.star_arg.entry.cname,
                Naming.args_cname))
            self.star_arg.entry.xdecref_cleanup = 0