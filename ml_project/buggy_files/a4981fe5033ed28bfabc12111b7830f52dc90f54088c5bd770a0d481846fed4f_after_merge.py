    def op_count(
        self, op_type: Optional[str] = None, precision: Optional[int] = None
    ) -> Optional[int]:
        if op_type != "mac":
            raise ValueError("Currently only counting of MAC-operations is supported.")

        if (
            isinstance(self._layer, op_count_supported_layer_types)
            and self.output_pixels
        ):
            count = 0
            for op in self.op_profiles:
                if (precision is None or op.precision == precision) and (
                    op_type is None or op.op_type == op_type
                ):
                    count += op.n
            return count
        return None