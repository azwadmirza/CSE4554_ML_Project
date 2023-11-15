    def compile_atom(self, atom_type, atom):
        if atom_type in _compile_table:
            ret = _compile_table[atom_type](self, atom)
            if not isinstance(ret, Result):
                ret = Result() + ret
            return ret
        if not isinstance(atom, HyObject):
            atom = wrap_value(atom)
            if isinstance(atom, HyObject):
                spoof_positions(atom)
                return self.compile_atom(type(atom), atom)