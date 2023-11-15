    def _replace_list(
        self,
        src_list: List[Any],
        dest_list: List[Any],
        masks: List[np.ndarray],
        inplace: bool = False,
        regex: bool = False,
    ) -> List["Block"]:
        """
        See BlockManager._replace_list docstring.
        """
        src_len = len(src_list) - 1

        rb = [self if inplace else self.copy()]
        for i, (src, dest) in enumerate(zip(src_list, dest_list)):
            new_rb: List["Block"] = []
            for blk in rb:
                m = masks[i][blk.mgr_locs.indexer]
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