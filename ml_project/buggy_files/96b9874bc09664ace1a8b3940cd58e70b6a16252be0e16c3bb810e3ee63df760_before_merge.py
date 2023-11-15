    def _ScanCode(self, co, module, deferredImports, topLevel = True):
        """Scan code, looking for imported modules and keeping track of the
           constants that have been created in order to better tell which
           modules are truly missing."""
        opIndex = 0
        arguments = []
        code = co.co_code
        numOps = len(code)
        is3 = sys.version_info[0] >= 3
        while opIndex < numOps:
            if is3:
                op = code[opIndex]
            else:
                op = ord(code[opIndex])
            opIndex += 1
            if op >= dis.HAVE_ARGUMENT:
                if is3:
                    opArg = code[opIndex] + code[opIndex + 1] * 256
                else:
                    opArg = ord(code[opIndex]) + ord(code[opIndex + 1]) * 256
                opIndex += 2
            
            if op == LOAD_CONST:
                # Store an argument to be used later by an IMPORT_NAME operation.
                arguments.append(co.co_consts[opArg])
            
            elif op == IMPORT_NAME:
                name = co.co_names[opArg]
                if len(arguments) >= 2:
                    relativeImportIndex, fromList = arguments[-2:]
                else:
                    relativeImportIndex = -1
                    fromList, = arguments
                
                if name not in module.excludeNames:
                    # Load the imported module
                    importedModule = self._ImportModule(name, deferredImports,
                            module, relativeImportIndex)
                    if importedModule is not None:
                        if fromList and fromList != ("*",) \
                                and importedModule.path is not None:
                            self._EnsureFromList(module, importedModule,
                                    fromList, deferredImports)
            
            elif op == IMPORT_FROM and topLevel:
                if is3:
                    op = code[opIndex]
                    opArg = code[opIndex + 1] + code[opIndex + 2] * 256
                else:
                    op = ord(code[opIndex])
                    opArg = ord(code[opIndex + 1]) + \
                            ord(code[opIndex + 2]) * 256
                opIndex += 3
                if op == STORE_FAST:
                    name = co.co_varnames[opArg]
                else:
                    name = co.co_names[opArg]
                storeName = True
                if deferredImports:
                    deferredCaller, deferredPackage, deferredFromList = \
                            deferredImports[-1]
                    storeName = deferredCaller is not module
                if storeName:
                    module.globalNames[name] = None
            
            elif op == IMPORT_STAR and topLevel and importedModule is not None:
                module.globalNames.update(importedModule.globalNames)
                arguments = []
            
            elif op not in (BUILD_LIST, INPLACE_ADD):
                # The stack was used for something else, so we clear it.
                if topLevel and op in STORE_OPS:
                    name = co.co_names[opArg]
                    module.globalNames[name] = None
                arguments = []
        
        # Scan the code objects from function & class definitions
        for constant in co.co_consts:
            if isinstance(constant, type(co)):
                self._ScanCode(constant, module, deferredImports,
                        topLevel = False)