    def slice_file(
        cls, raw_str: str, templated_str: str, config=None
    ) -> Tuple[List[RawFileSlice], List[TemplatedFileSlice], str]:
        """Slice the file to determine regions where we can fix."""
        templater_logger.info("Slicing File Template")
        templater_logger.debug("    Raw String: %r", raw_str)
        templater_logger.debug("    Templated String: %r", templated_str)
        # Slice the raw file
        raw_sliced = list(cls._slice_template(raw_str))
        # Find the literals
        literals = [
            raw_slice.raw
            for raw_slice in raw_sliced
            if raw_slice.slice_type == "literal"
        ]
        templater_logger.debug("    Literals: %s", literals)
        for loop_idx in range(2):
            templater_logger.debug("    # Slice Loop %s", loop_idx)
            # Calculate occurrences
            raw_occurrences = cls._substring_occurances(raw_str, literals)
            templated_occurances = cls._substring_occurances(templated_str, literals)
            templater_logger.debug(
                "    Occurances: Raw: %s, Templated: %s",
                raw_occurrences,
                templated_occurances,
            )
            # Split on invariants
            split_sliced = list(
                cls._split_invariants(
                    raw_sliced,
                    literals,
                    raw_occurrences,
                    templated_occurances,
                    templated_str,
                )
            )
            templater_logger.debug("    Split Sliced: %s", split_sliced)
            # Deal with uniques and coalesce the rest
            sliced_file = list(
                cls._split_uniques_coalesce_rest(
                    split_sliced, raw_occurrences, templated_occurances, templated_str
                )
            )
            templater_logger.debug("    Fully Sliced: %s", sliced_file)
            unwrap_wrapped = (
                True
                if config is None
                else config.get(
                    "unwrap_wrapped_queries", section="templater", default=True
                )
            )
            sliced_file, new_templated_str = cls._check_for_wrapped(
                sliced_file, templated_str, unwrap_wrapped=unwrap_wrapped
            )
            if new_templated_str == templated_str:
                # If we didn't change it then we're done.
                break
            else:
                # If it's not equal, loop around
                templated_str = new_templated_str
        return raw_sliced, sliced_file, new_templated_str