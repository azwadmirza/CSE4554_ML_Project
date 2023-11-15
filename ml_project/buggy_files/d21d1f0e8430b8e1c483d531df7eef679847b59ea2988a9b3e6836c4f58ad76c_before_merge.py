    def generate_module_preamble(self, env, options, cimported_modules, metadata, code):
        code.put_generated_by()
        if metadata:
            code.putln("/* BEGIN: Cython Metadata")
            code.putln(json.dumps(metadata, indent=4, sort_keys=True))
            code.putln("END: Cython Metadata */")
            code.putln("")
        code.putln("#define PY_SSIZE_T_CLEAN")

        for inc in sorted(env.c_includes.values(), key=IncludeCode.sortkey):
            if inc.location == inc.INITIAL:
                inc.write(code)
        code.putln("#ifndef Py_PYTHON_H")
        code.putln("    #error Python headers needed to compile C extensions, "
                   "please install development version of Python.")
        code.putln("#elif PY_VERSION_HEX < 0x02060000 || "
                   "(0x03000000 <= PY_VERSION_HEX && PY_VERSION_HEX < 0x03030000)")
        code.putln("    #error Cython requires Python 2.6+ or Python 3.3+.")
        code.putln("#else")
        code.globalstate["end"].putln("#endif /* Py_PYTHON_H */")

        from .. import __version__
        code.putln('#define CYTHON_ABI "%s"' % __version__.replace('.', '_'))
        code.putln('#define CYTHON_HEX_VERSION %s' % build_hex_version(__version__))
        code.putln("#define CYTHON_FUTURE_DIVISION %d" % (
            Future.division in env.context.future_directives))

        self._put_setup_code(code, "CModulePreamble")
        if env.context.options.cplus:
            self._put_setup_code(code, "CppInitCode")
        else:
            self._put_setup_code(code, "CInitCode")
        self._put_setup_code(code, "PythonCompatibility")
        self._put_setup_code(code, "MathInitCode")

        if options.c_line_in_traceback:
            cinfo = "%s = %s; " % (Naming.clineno_cname, Naming.line_c_macro)
        else:
            cinfo = ""
        code.put("""
#define __PYX_ERR(f_index, lineno, Ln_error) \\
{ \\
  %s = %s[f_index]; %s = lineno; %sgoto Ln_error; \\
}
""" % (Naming.filename_cname, Naming.filetable_cname, Naming.lineno_cname, cinfo))

        code.putln("")
        self.generate_extern_c_macro_definition(code)
        code.putln("")

        code.putln("#define %s" % Naming.h_guard_prefix + self.api_name(env))
        code.putln("#define %s" % Naming.api_guard_prefix + self.api_name(env))
        code.putln("/* Early includes */")
        self.generate_includes(env, cimported_modules, code, late=False)
        code.putln("")
        code.putln("#if defined(PYREX_WITHOUT_ASSERTIONS) && !defined(CYTHON_WITHOUT_ASSERTIONS)")
        code.putln("#define CYTHON_WITHOUT_ASSERTIONS")
        code.putln("#endif")
        code.putln("")

        if env.directives['ccomplex']:
            code.putln("")
            code.putln("#if !defined(CYTHON_CCOMPLEX)")
            code.putln("#define CYTHON_CCOMPLEX 1")
            code.putln("#endif")
            code.putln("")
        code.put(UtilityCode.load_as_string("UtilityFunctionPredeclarations", "ModuleSetupCode.c")[0])

        c_string_type = env.directives['c_string_type']
        c_string_encoding = env.directives['c_string_encoding']
        if c_string_type not in ('bytes', 'bytearray') and not c_string_encoding:
            error(self.pos, "a default encoding must be provided if c_string_type is not a byte type")
        code.putln('#define __PYX_DEFAULT_STRING_ENCODING_IS_ASCII %s' % int(c_string_encoding == 'ascii'))
        if c_string_encoding == 'default':
            code.putln('#define __PYX_DEFAULT_STRING_ENCODING_IS_DEFAULT 1')
        else:
            code.putln('#define __PYX_DEFAULT_STRING_ENCODING_IS_DEFAULT 0')
            code.putln('#define __PYX_DEFAULT_STRING_ENCODING "%s"' % c_string_encoding)
        if c_string_type == 'bytearray':
            c_string_func_name = 'ByteArray'
        else:
            c_string_func_name = c_string_type.title()
        code.putln('#define __Pyx_PyObject_FromString __Pyx_Py%s_FromString' % c_string_func_name)
        code.putln('#define __Pyx_PyObject_FromStringAndSize __Pyx_Py%s_FromStringAndSize' % c_string_func_name)
        code.put(UtilityCode.load_as_string("TypeConversions", "TypeConversion.c")[0])

        # These utility functions are assumed to exist and used elsewhere.
        PyrexTypes.c_long_type.create_to_py_utility_code(env)
        PyrexTypes.c_long_type.create_from_py_utility_code(env)
        PyrexTypes.c_int_type.create_from_py_utility_code(env)

        code.put(Nodes.branch_prediction_macros)
        code.putln('static CYTHON_INLINE void __Pyx_pretend_to_initialize(void* ptr) { (void)ptr; }')
        code.putln('')
        code.putln('static PyObject *%s = NULL;' % env.module_cname)
        code.putln('static PyObject *%s;' % env.module_dict_cname)
        code.putln('static PyObject *%s;' % Naming.builtins_cname)
        code.putln('static PyObject *%s = NULL;' % Naming.cython_runtime_cname)
        code.putln('static PyObject *%s;' % Naming.empty_tuple)
        code.putln('static PyObject *%s;' % Naming.empty_bytes)
        code.putln('static PyObject *%s;' % Naming.empty_unicode)
        if Options.pre_import is not None:
            code.putln('static PyObject *%s;' % Naming.preimport_cname)
        code.putln('static int %s;' % Naming.lineno_cname)
        code.putln('static int %s = 0;' % Naming.clineno_cname)
        code.putln('static const char * %s= %s;' % (Naming.cfilenm_cname, Naming.file_c_macro))
        code.putln('static const char *%s;' % Naming.filename_cname)

        env.use_utility_code(UtilityCode.load_cached("FastTypeChecks", "ModuleSetupCode.c"))
        if has_np_pythran(env):
            env.use_utility_code(UtilityCode.load_cached("PythranConversion", "CppSupport.cpp"))