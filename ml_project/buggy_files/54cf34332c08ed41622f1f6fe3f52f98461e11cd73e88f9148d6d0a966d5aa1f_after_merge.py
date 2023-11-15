    def _replace_list(
        self,
        src_list: List[Any],
        dest_list: List[Any],
        inplace: bool = False,
        regex: bool = False,
    ) -> List["Block"]:
        """
        See BlockManager._replace_list docstring.
        """
        src_len = len(src_list) - 1

        def comp(s: Scalar, mask: np.ndarray, regex: bool = False) -> np.ndarray:
            """
            Generate a bool array by perform an equality check, or perform
            an element-wise regular expression matching
            """
            if isna(s):
                return ~mask

            s = com.maybe_box_datetimelike(s)
            return compare_or_regex_search(self.values, s, regex, mask)

        # Calculate the mask once, prior to the call of comp
        # in order to avoid repeating the same computations
        mask = ~isna(self.values)

        masks = [comp(s, mask, regex) for s in src_list]

        rb = [self if inplace else self.copy()]
        for i, (src, dest) in enumerate(zip(src_list, dest_list)):
            new_rb: List["Block"] = []
            for blk in rb:
                m = masks[i]
                convert = i == src_len  # only convert once at the end
                result = blk._replace_coerce(
                    mask=m,
                    to_replace=src,
                    value=dest,
                    inplace=inplace,
                    convert=convert,
                    regex=regex,
                )
                if m.any() or convert:
                    if isinstance(result, list):
                        new_rb.extend(result)
                    else:
                        new_rb.append(result)
                else:
                    new_rb.append(blk)
            rb = new_rb
        return rb