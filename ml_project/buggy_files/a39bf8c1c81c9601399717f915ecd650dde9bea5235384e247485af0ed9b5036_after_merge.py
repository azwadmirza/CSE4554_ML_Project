    def get_probability_map(self, subject: Subject) -> torch.Tensor:
        label_map_tensor = self.get_probability_map_image(subject).data.float()

        if self.label_probabilities_dict is None:
            return label_map_tensor > 0
        probability_map = self.get_probabilities_from_label_map(
            label_map_tensor,
            self.label_probabilities_dict,
            self.patch_size,
        )
        return probability_map