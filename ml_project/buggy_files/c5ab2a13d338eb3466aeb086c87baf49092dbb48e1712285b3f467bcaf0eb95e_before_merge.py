    def _get_source_code(
        self, contract: Contract
    ):  # pylint: disable=too-many-branches,too-many-statements
        """
        Save the source code of the contract in self._source_codes
        Patch the source code
        :param contract:
        :return:
        """
        src_mapping = contract.source_mapping
        content = self._slither.source_code[src_mapping["filename_absolute"]].encode("utf8")
        start = src_mapping["start"]
        end = src_mapping["start"] + src_mapping["length"]

        to_patch = []
        # interface must use external
        if self._external_to_public and contract.contract_kind != "interface":
            for f in contract.functions_declared:
                # fallback must be external
                if f.is_fallback or f.is_constructor_variables:
                    continue
                if f.visibility == "external":
                    attributes_start = (
                        f.parameters_src.source_mapping["start"]
                        + f.parameters_src.source_mapping["length"]
                    )
                    attributes_end = f.returns_src.source_mapping["start"]
                    attributes = content[attributes_start:attributes_end]
                    regex = re.search(r"((\sexternal)\s+)|(\sexternal)$|(\)external)$", attributes)
                    if regex:
                        to_patch.append(
                            Patch(
                                attributes_start + regex.span()[0] + 1,
                                "public_to_external",
                            )
                        )
                    else:
                        raise SlitherException(f"External keyword not found {f.name} {attributes}")

                    for var in f.parameters:
                        if var.location == "calldata":
                            calldata_start = var.source_mapping["start"]
                            calldata_end = calldata_start + var.source_mapping["length"]
                            calldata_idx = content[calldata_start:calldata_end].find(" calldata ")
                            to_patch.append(
                                Patch(
                                    calldata_start + calldata_idx + 1,
                                    "calldata_to_memory",
                                )
                            )

        if self._private_to_internal:
            for variable in contract.state_variables_declared:
                if variable.visibility == "private":
                    print(variable.source_mapping)
                    attributes_start = variable.source_mapping["start"]
                    attributes_end = attributes_start + variable.source_mapping["length"]
                    attributes = content[attributes_start:attributes_end]
                    print(attributes)
                    regex = re.search(r" private ", attributes)
                    if regex:
                        to_patch.append(
                            Patch(
                                attributes_start + regex.span()[0] + 1,
                                "private_to_internal",
                            )
                        )
                    else:
                        raise SlitherException(
                            f"private keyword not found {variable.name} {attributes}"
                        )

        if self._remove_assert:
            for function in contract.functions_and_modifiers_declared:
                for node in function.nodes:
                    for ir in node.irs:
                        if isinstance(ir, SolidityCall) and ir.function == SolidityFunction(
                            "assert(bool)"
                        ):
                            to_patch.append(Patch(node.source_mapping["start"], "line_removal"))
                            logger.info(
                                f"Code commented: {node.expression} ({node.source_mapping_str})"
                            )

        to_patch.sort(key=lambda x: x.index, reverse=True)

        content = content[start:end]
        for patch in to_patch:
            patch_type = patch.patch_type
            index = patch.index
            index = index - start
            if patch_type == "public_to_external":
                content = content[:index] + "public" + content[index + len("external") :]
            if patch_type == "private_to_internal":
                content = content[:index] + "internal" + content[index + len("private") :]
            elif patch_type == "calldata_to_memory":
                content = content[:index] + "memory" + content[index + len("calldata") :]
            else:
                assert patch_type == "line_removal"
                content = content[:index] + " // " + content[index:]

        self._source_codes[contract] = content.decode("utf8")