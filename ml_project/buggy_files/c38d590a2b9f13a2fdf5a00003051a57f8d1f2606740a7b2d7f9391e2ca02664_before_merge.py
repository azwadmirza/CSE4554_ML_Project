    def clear_pymathics_modules(self):
        from mathics.builtin import builtins, builtins_by_module
        # Remove all modules that are not in mathics
        # print("cleaning pymathics modules")
        for key in list(builtins_by_module.keys()):
            if key[:8] != "mathics.":
                print("removing module ", key, " not in mathics.")
                del builtins_by_module[key]
        # print("reloading symbols from current builtins.")
        for s in self.pymathics:
            if s in self.builtin:
                # If there was a true built-in definition for the symbol, restore it, else, remove he symbol. 
                if self.pymathics[s]:
                    self.builtin[s] = self.pymathics[s]
                    builtins[s] = None
                    for key, val in builtins_by_module:
                        for simb in val:
                            if simb.get_name() == s:
                                builtins[s] = simb
                                break
                        if builtins[s] is not None:
                            break
                    if builtins[s] is None:
                        builtins.__delitem__(s)
                else:
                    self.builtin.__delitem__(s)
                    builtins.__delitem__(s)
        self.pymathics = {}
        # print("everything is clean")
        return None