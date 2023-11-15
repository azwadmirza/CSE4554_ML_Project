    def generate_type_ready_code(self, env, entry, code):
        # Generate a call to PyType_Ready for an extension
        # type defined in this module.
        type = entry.type
        typeobj_cname = type.typeobj_cname
        scope = type.scope
        if scope: # could be None if there was an error
            if entry.visibility != 'extern':
                for slot in TypeSlots.slot_table:
                    slot.generate_dynamic_init_code(scope, code)
                code.putln(
                    "if (PyType_Ready(&%s) < 0) %s" % (
                        typeobj_cname,
                        code.error_goto(entry.pos)))
                # Don't inherit tp_print from builtin types, restoring the
                # behavior of using tp_repr or tp_str instead.
                code.putln("%s.tp_print = 0;" % typeobj_cname)
                # Fix special method docstrings. This is a bit of a hack, but
                # unless we let PyType_Ready create the slot wrappers we have
                # a significant performance hit. (See trac #561.)
                for func in entry.type.scope.pyfunc_entries:
                    is_buffer = func.name in ('__getbuffer__', '__releasebuffer__')
                    if (func.is_special and Options.docstrings and
                            func.wrapperbase_cname and not is_buffer):
                        slot = TypeSlots.method_name_to_slot[func.name]
                        preprocessor_guard = slot.preprocessor_guard_code()
                        if preprocessor_guard:
                            code.putln(preprocessor_guard)
                        code.putln('#if CYTHON_COMPILING_IN_CPYTHON')
                        code.putln("{")
                        code.putln(
                            'PyObject *wrapper = PyObject_GetAttrString((PyObject *)&%s, "%s"); %s' % (
                                typeobj_cname,
                                func.name,
                                code.error_goto_if_null('wrapper', entry.pos)))
                        code.putln(
                            "if (Py_TYPE(wrapper) == &PyWrapperDescr_Type) {")
                        code.putln(
                            "%s = *((PyWrapperDescrObject *)wrapper)->d_base;" % (
                                func.wrapperbase_cname))
                        code.putln(
                            "%s.doc = %s;" % (func.wrapperbase_cname, func.doc_cname))
                        code.putln(
                            "((PyWrapperDescrObject *)wrapper)->d_base = &%s;" % (
                                func.wrapperbase_cname))
                        code.putln("}")
                        code.putln("}")
                        code.putln('#endif')
                        if preprocessor_guard:
                            code.putln('#endif')
                if type.vtable_cname:
                    code.putln(
                        "if (__Pyx_SetVtable(%s.tp_dict, %s) < 0) %s" % (
                            typeobj_cname,
                            type.vtabptr_cname,
                            code.error_goto(entry.pos)))
                    code.globalstate.use_utility_code(
                        UtilityCode.load_cached('SetVTable', 'ImportExport.c'))
                if not type.scope.is_internal and not type.scope.directives['internal']:
                    # scope.is_internal is set for types defined by
                    # Cython (such as closures), the 'internal'
                    # directive is set by users
                    code.putln(
                        'if (PyObject_SetAttrString(%s, "%s", (PyObject *)&%s) < 0) %s' % (
                            Naming.module_cname,
                            scope.class_name,
                            typeobj_cname,
                            code.error_goto(entry.pos)))
                weakref_entry = scope.lookup_here("__weakref__") if not scope.is_closure_class_scope else None
                if weakref_entry:
                    if weakref_entry.type is py_object_type:
                        tp_weaklistoffset = "%s.tp_weaklistoffset" % typeobj_cname
                        if type.typedef_flag:
                            objstruct = type.objstruct_cname
                        else:
                            objstruct = "struct %s" % type.objstruct_cname
                        code.putln("if (%s == 0) %s = offsetof(%s, %s);" % (
                            tp_weaklistoffset,
                            tp_weaklistoffset,
                            objstruct,
                            weakref_entry.cname))
                    else:
                        error(weakref_entry.pos, "__weakref__ slot must be of type 'object'")
                if scope.lookup_here("__reduce_cython__") if not scope.is_closure_class_scope else None:
                    # Unfortunately, we cannot reliably detect whether a
                    # superclass defined __reduce__ at compile time, so we must
                    # do so at runtime.
                    code.globalstate.use_utility_code(
                        UtilityCode.load_cached('SetupReduce', 'ExtensionTypes.c'))
                    code.putln('if (__Pyx_setup_reduce((PyObject*)&%s) < 0) %s' % (
                                  typeobj_cname,
                                  code.error_goto(entry.pos)))