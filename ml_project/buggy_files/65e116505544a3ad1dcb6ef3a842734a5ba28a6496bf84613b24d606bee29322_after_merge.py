    def fix_prec(self, *args, **kwargs):
        if self.is_wrapper:
            self.child = self.child.fix_prec(*args, **kwargs)
            return self
        else:
            base = kwargs.get("base", 10)
            prec_fractional = kwargs.get("precision_fractional", 3)
            max_precision = _get_maximum_precision()
            if self._requires_large_precision(max_precision, base, prec_fractional):
                return (
                    syft.LargePrecisionTensor(*args, **kwargs)
                    .on(self)
                    .child.fix_large_precision()
                    .wrap()
                )
            else:
                return syft.FixedPrecisionTensor(*args, **kwargs).on(self).enc_fix_prec().wrap()