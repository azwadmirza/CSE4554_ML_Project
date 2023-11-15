    def replace_list(
        self: T,
        src_list: List[Any],
        dest_list: List[Any],
        inplace: bool = False,
        regex: bool = False,
    ) -> T:
        """ do a list replace """
        inplace = validate_bool_kwarg(inplace, "inplace")

        # figure out our mask apriori to avoid repeated replacements
        values = self.as_array()

        def comp(s: Scalar, mask: np.ndarray, regex: bool = False):
            """
            Generate a bool array by perform an equality check, or perform
            an element-wise regular expression matching
            """
            if isna(s):
                return ~mask

            s = com.maybe_box_datetimelike(s)
            return _compare_or_regex_search(values, s, regex, mask)

        # Calculate the mask once, prior to the call of comp
        # in order to avoid repeating the same computations
        mask = ~isna(values)

        masks = [comp(s, mask, regex) for s in src_list]

        bm = self.apply(
            "_replace_list",
            src_list=src_list,
            dest_list=dest_list,
            masks=masks,
            inplace=inplace,
            regex=regex,
        )
        bm._consolidate_inplace()
        return bm