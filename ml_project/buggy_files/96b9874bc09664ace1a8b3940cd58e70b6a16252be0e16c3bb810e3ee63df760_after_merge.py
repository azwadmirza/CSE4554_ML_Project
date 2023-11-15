    def _ScanCode(self, co, module, deferredImports, topLevel = True):
        """Scan code, looking for imported modules and keeping track of the
           constants that have been created in order to better tell which
           modules are truly missing."""
        arguments = []
        importedModule = None
        method = dis._unpack_opargs if sys.version_info[:2] >= (3, 5) \
                else self._UnpackOpArgs
        for opIndex, op, opArg in method(co.co_code):

            # keep track of constants (these are used for importing)
            # immediately restart loop so arguments are retained
            if op == LOAD_CONST:
                arguments.append(co.co_consts[opArg])
                continue

            # import statement: attempt to import module
            elif op == IMPORT_NAME:
                name = co.co_names[opArg]
                if len(arguments) >= 2:
                    relativeImportIndex, fromList = arguments[-2:]
                else:
                    relativeImportIndex = -1
                    fromList, = arguments
                if name not in module.excludeNames:
                    importedModule = self._ImportModule(name, deferredImports,
                            module, relativeImportIndex)
                    if importedModule is not None:
                        if fromList and fromList != ("*",) \
                                and importedModule.path is not None:
                            self._EnsureFromList(module, importedModule,
                                    fromList, deferredImports)

            # import * statement: copy all global names
            elif op == IMPORT_STAR and topLevel and importedModule is not None:
                module.globalNames.update(importedModule.globalNames)

            # store operation: track only top level
            elif topLevel and op in STORE_OPS:
                name = co.co_names[opArg]
                module.globalNames[name] = None

            # reset arguments; these are only needed for import statements so
            # ignore them in all other cases!
            arguments = []

        # Scan the code objects from function & class definitions
        for constant in co.co_consts:
            if isinstance(constant, type(co)):
                self._ScanCode(constant, module, deferredImports,
                        topLevel = False)