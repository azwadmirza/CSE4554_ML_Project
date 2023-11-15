    def set_cell_anchors(self, dtype, device):
        # type: (int, Device) -> None    # noqa: F821
        if self.cell_anchors is not None:
            return

        cell_anchors = [
            self.generate_anchors(
                sizes,
                aspect_ratios,
                dtype,
                device
            )
            for sizes, aspect_ratios in zip(self.sizes, self.aspect_ratios)
        ]
        self.cell_anchors = cell_anchors