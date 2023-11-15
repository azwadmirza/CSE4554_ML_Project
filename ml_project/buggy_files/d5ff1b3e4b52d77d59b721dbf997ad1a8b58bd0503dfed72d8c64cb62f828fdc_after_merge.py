        def core(typ):
            out = self.find_matching_getattr_template(typ, attr)
            if out:
                return out['return_type']