    def unify(self, typingctx, other):
        if isinstance(other, List):
            dtype = typingctx.unify_pairs(self.dtype, other.dtype)
            reflected = self.reflected or other.reflected
            if dtype is not None:
                siv = self.initial_value
                oiv = other.initial_value
                if siv is not None and oiv is not None:
                    use = siv
                    if siv is None:
                        use = oiv
                    return List(dtype, reflected, use)
                else:
                    return List(dtype, reflected)