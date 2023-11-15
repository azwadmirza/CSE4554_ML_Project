    def train(
            cls,
            images_paths: Sequence[TypePath],
            cutoff: Optional[Tuple[float, float]] = None,
            mask_path: Optional[TypePath] = None,
            masking_function: Optional[Callable] = None,
            output_path: Optional[TypePath] = None,
            ) -> np.ndarray:
        """Extract average histogram landmarks from images used for training.

        Args:
            images_paths: List of image paths used to train.
            cutoff: Optional minimum and maximum quantile values,
                respectively, that are used to select a range of intensity of
                interest. Equivalent to :math:`pc_1` and :math:`pc_2` in
                `Nyúl and Udupa's paper <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.204.102&rep=rep1&type=pdf>`_.
            mask_path: Optional path to a mask image to extract voxels used for
                training.
            masking_function: Optional function used to extract voxels used for
                training.
            output_path: Optional file path with extension ``.txt`` or
                ``.npy``, where the landmarks will be saved.

        Example:

            >>> import torch
            >>> import numpy as np
            >>> from pathlib import Path
            >>> from torchio.transforms import HistogramStandardization
            >>>
            >>> t1_paths = ['subject_a_t1.nii', 'subject_b_t1.nii.gz']
            >>> t2_paths = ['subject_a_t2.nii', 'subject_b_t2.nii.gz']
            >>>
            >>> t1_landmarks_path = Path('t1_landmarks.npy')
            >>> t2_landmarks_path = Path('t2_landmarks.npy')
            >>>
            >>> t1_landmarks = (
            ...     t1_landmarks_path
            ...     if t1_landmarks_path.is_file()
            ...     else HistogramStandardization.train(t1_paths)
            ... )
            >>> torch.save(t1_landmarks, t1_landmarks_path)
            >>>
            >>> t2_landmarks = (
            ...     t2_landmarks_path
            ...     if t2_landmarks_path.is_file()
            ...     else HistogramStandardization.train(t2_paths)
            ... )
            >>> torch.save(t2_landmarks, t2_landmarks_path)
            >>>
            >>> landmarks_dict = {
            ...     't1': t1_landmarks,
            ...     't2': t2_landmarks,
            ... }
            >>>
            >>> transform = HistogramStandardization(landmarks_dict)
        """  # noqa: E501
        quantiles_cutoff = DEFAULT_CUTOFF if cutoff is None else cutoff
        percentiles_cutoff = 100 * np.array(quantiles_cutoff)
        percentiles_database = []
        percentiles = _get_percentiles(percentiles_cutoff)
        for image_file_path in tqdm(images_paths):
            tensor, _ = read_image(image_file_path)
            if masking_function is not None:
                mask = masking_function(tensor)
            else:
                if mask_path is not None:
                    mask, _ = read_image(mask_path)
                    mask = mask.numpy() > 0
                else:
                    mask = np.ones_like(tensor, dtype=np.bool)
            array = tensor.numpy()
            percentile_values = np.percentile(array[mask], percentiles)
            percentiles_database.append(percentile_values)
        percentiles_database = np.vstack(percentiles_database)
        mapping = _get_average_mapping(percentiles_database)

        if output_path is not None:
            output_path = Path(output_path).expanduser()
            extension = output_path.suffix
            if extension == '.txt':
                modality = 'image'
                text = f'{modality} {" ".join(map(str, mapping))}'
                output_path.write_text(text)
            elif extension == '.npy':
                np.save(output_path, mapping)
        return mapping