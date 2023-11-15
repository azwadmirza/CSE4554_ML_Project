    def binarize_with_mask(self, txt, prefix, suffix, leading_space, trailing_space):
        toks = self.binarize(
            prefix + leading_space + txt + trailing_space + suffix,
            append_eos=True,
        )
        mask = torch.zeros_like(toks, dtype=torch.bool)
        mask_start = len(self.binarize(prefix))
        mask_size = len(self.binarize(leading_space + txt))
        mask[mask_start:mask_start + mask_size] = 1
        return toks, mask