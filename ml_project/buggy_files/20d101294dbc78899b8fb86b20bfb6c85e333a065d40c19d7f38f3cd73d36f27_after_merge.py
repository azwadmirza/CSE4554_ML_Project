    def _set_inoutput_item(self, item, output=False, name=None):
        """
        Set an item to be input or output.

        Arguments
        item     -- the item
        inoutput -- a Namedlist of either input or output items
        name     -- an optional name for the item
        """
        inoutput = self.output if output else self.input
        # Check to see if the item is a path, if so, just make it a string
        if isinstance(item, Path):
            item = str(item)
        if isinstance(item, str):
            item = self.apply_default_remote(item)

            # Check to see that all flags are valid
            # Note that "remote", "dynamic", and "expand" are valid for both inputs and outputs.
            if isinstance(item, AnnotatedString):
                for flag in item.flags:
                    if not output and flag in [
                        "protected",
                        "temp",
                        "temporary",
                        "directory",
                        "touch",
                        "pipe",
                    ]:
                        logger.warning(
                            "The flag '{}' used in rule {} is only valid for outputs, not inputs.".format(
                                flag, self
                            )
                        )
                    if output and flag in ["ancient"]:
                        logger.warning(
                            "The flag '{}' used in rule {} is only valid for inputs, not outputs.".format(
                                flag, self
                            )
                        )

            # add the rule to the dependencies
            if isinstance(item, _IOFile) and item.rule and item in item.rule.output:
                self.dependencies[item] = item.rule
            if output:
                item = self._update_item_wildcard_constraints(item)
            else:
                if (
                    contains_wildcard_constraints(item)
                    and self.workflow.mode != Mode.subprocess
                ):
                    logger.warning("Wildcard constraints in inputs are ignored.")
            # record rule if this is an output file output
            _item = IOFile(item, rule=self)
            if is_flagged(item, "temp"):
                if output:
                    self.temp_output.add(_item)
            if is_flagged(item, "protected"):
                if output:
                    self.protected_output.add(_item)
            if is_flagged(item, "touch"):
                if output:
                    self.touch_output.add(_item)
            if is_flagged(item, "dynamic"):
                if output:
                    self.dynamic_output.add(_item)
                else:
                    self.dynamic_input.add(_item)
            if is_flagged(item, "report"):
                report_obj = item.flags["report"]
                if report_obj.caption is not None:
                    r = ReportObject(
                        os.path.join(self.workflow.current_basedir, report_obj.caption),
                        report_obj.category,
                    )
                    item.flags["report"] = r
            if is_flagged(item, "subworkflow"):
                if output:
                    raise SyntaxError("Only input files may refer to a subworkflow")
                else:
                    # record the workflow this item comes from
                    sub = item.flags["subworkflow"]
                    if _item in self.subworkflow_input:
                        other = self.subworkflow_input[_item]
                        if sub != other:
                            raise WorkflowError(
                                "The input file {} is ambiguously "
                                "associated with two subworkflows "
                                "{} and {}.".format(item, sub, other),
                                rule=self,
                            )
                    self.subworkflow_input[_item] = sub
            inoutput.append(_item)
            if name:
                inoutput._add_name(name)
        elif callable(item):
            if output:
                raise SyntaxError("Only input files can be specified as functions")
            inoutput.append(item)
            if name:
                inoutput._add_name(name)
        else:
            try:
                start = len(inoutput)
                for i in item:
                    self._set_inoutput_item(i, output=output)
                if name:
                    # if the list was named, make it accessible
                    inoutput._set_name(name, start, end=len(inoutput))
            except TypeError:
                raise SyntaxError(
                    "Input and output files have to be specified as strings or lists of strings."
                )