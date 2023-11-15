    def replace_list(
        self: T,
        src_list: List[Any],
        dest_list: List[Any],
        inplace: bool = False,
        regex: bool = False,
    ) -> T:
        """ do a list replace """
        inplace = validate_bool_kwarg(inplace, "inplace")

        bm = self.apply(
            "_replace_list",
            src_list=src_list,
            dest_list=dest_list,
            inplace=inplace,
            regex=regex,
        )
        bm._consolidate_inplace()
        return bm