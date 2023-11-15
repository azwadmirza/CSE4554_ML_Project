    def get_probabilities_from_label_map(
            label_map: torch.Tensor,
            label_probabilities_dict: Dict[int, float],
            patch_size: np.ndarray,
            ) -> torch.Tensor:
        """Create probability map according to label map probabilities."""
        patch_size = patch_size.astype(int)
        ini_i, ini_j, ini_k = patch_size // 2
        spatial_shape = np.array(label_map.shape[1:])
        if np.any(patch_size > spatial_shape):
            message = (
                f'Patch size {patch_size}'
                f'larger than label map {spatial_shape}'
            )
            raise RuntimeError(message)
        crop_fin_i, crop_fin_j, crop_fin_k = crop_fin = (patch_size - 1) // 2
        fin_i, fin_j, fin_k = spatial_shape - crop_fin
        # See https://github.com/fepegar/torchio/issues/458
        label_map = label_map[:, ini_i:fin_i, ini_j:fin_j, ini_k:fin_k]

        multichannel = label_map.shape[0] > 1
        probability_map = torch.zeros_like(label_map)
        label_probs = torch.Tensor(list(label_probabilities_dict.values()))
        normalized_probs = label_probs / label_probs.sum()
        iterable = zip(label_probabilities_dict, normalized_probs)
        for label, label_probability in iterable:
            if multichannel:
                mask = label_map[label]
            else:
                mask = label_map == label
            label_size = mask.sum()
            if not label_size:
                continue
            prob_voxels = label_probability / label_size
            if multichannel:
                probability_map[label] = prob_voxels * mask
            else:
                probability_map[mask] = prob_voxels
        if multichannel:
            probability_map = probability_map.sum(dim=0, keepdim=True)

        # See https://github.com/fepegar/torchio/issues/458
        padding = ini_k, crop_fin_k, ini_j, crop_fin_j, ini_i, crop_fin_i
        probability_map = torch.nn.functional.pad(
            probability_map,
            padding,
        )
        return probability_map