    def __call__(
        self,
        data_array: np.ndarray,
        affine=None,
        mode: Optional[Union[GridSampleMode, str]] = None,
        padding_mode: Optional[Union[GridSamplePadMode, str]] = None,
        dtype: Optional[np.dtype] = None,
    ):
        """
        Args:
            data_array: in shape (num_channels, H[, W, ...]).
            affine (matrix): (N+1)x(N+1) original affine matrix for spatially ND `data_array`. Defaults to identity.
            mode: {``"bilinear"``, ``"nearest"``}
                Interpolation mode to calculate output values. Defaults to ``self.mode``.
                See also: https://pytorch.org/docs/stable/nn.functional.html#grid-sample
            padding_mode: {``"zeros"``, ``"border"``, ``"reflection"``}
                Padding mode for outside grid values. Defaults to ``self.padding_mode``.
                See also: https://pytorch.org/docs/stable/nn.functional.html#grid-sample
            dtype: output array data type. Defaults to ``self.dtype``.

        Raises:
            ValueError: When ``data_array`` has no spatial dimensions.
            ValueError: When ``pixdim`` is nonpositive.

        Returns:
            data_array (resampled into `self.pixdim`), original pixdim, current pixdim.

        """
        sr = data_array.ndim - 1
        if sr <= 0:
            raise ValueError("data_array must have at least one spatial dimension.")
        if affine is None:
            # default to identity
            affine = np.eye(sr + 1, dtype=np.float64)
            affine_ = np.eye(sr + 1, dtype=np.float64)
        else:
            affine_ = to_affine_nd(sr, affine)
        out_d = self.pixdim[:sr]
        if out_d.size < sr:
            out_d = np.append(out_d, [1.0] * (out_d.size - sr))
        if np.any(out_d <= 0):
            raise ValueError(f"pixdim must be positive, got {out_d}.")
        # compute output affine, shape and offset
        new_affine = zoom_affine(affine_, out_d, diagonal=self.diagonal)
        output_shape, offset = compute_shape_offset(data_array.shape[1:], affine_, new_affine)
        new_affine[:sr, -1] = offset[:sr]
        transform = np.linalg.inv(affine_) @ new_affine
        # adapt to the actual rank
        transform_ = to_affine_nd(sr, transform)
        _dtype = dtype or self.dtype or np.float32

        # no resampling if it's identity transform
        if np.allclose(transform_, np.diag(np.ones(len(transform_))), atol=1e-3):
            output_data = data_array.copy().astype(_dtype)
            new_affine = to_affine_nd(affine, new_affine)
            return output_data, affine, new_affine

        # resample
        affine_xform = AffineTransform(
            normalized=False,
            mode=mode or self.mode,
            padding_mode=padding_mode or self.padding_mode,
            align_corners=True,
            reverse_indexing=True,
        )
        output_data = affine_xform(
            torch.from_numpy((data_array.astype(np.float64))).unsqueeze(0),  # AffineTransform requires a batch dim
            torch.from_numpy(transform_.astype(np.float64)),
            spatial_size=output_shape,
        )
        output_data = output_data.squeeze(0).detach().cpu().numpy().astype(_dtype)
        new_affine = to_affine_nd(affine, new_affine)
        return output_data, affine, new_affine