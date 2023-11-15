    def transform(
        self,
        y: Union[pd.Series, np.ndarray, torch.Tensor],
        return_norm: bool = False,
        target_scale: torch.Tensor = None,
    ) -> Union[Tuple[Union[np.ndarray, torch.Tensor], np.ndarray], Union[np.ndarray, torch.Tensor]]:
        """
        Rescale data.

        Args:
            y (Union[pd.Series, np.ndarray, torch.Tensor]): input data
            return_norm (bool, optional): [description]. Defaults to False.
            target_scale (torch.Tensor): target scale to use instead of fitted center and scale

        Returns:
            Union[Tuple[Union[np.ndarray, torch.Tensor], np.ndarray], Union[np.ndarray, torch.Tensor]]: rescaled
                data with type depending on input type. returns second element if ``return_norm=True``
        """
        y = self._preprocess_y(y)
        # get center and scale
        if target_scale is None:
            target_scale = self.get_parameters().numpy()[None, :]
        center = target_scale[..., 0]
        scale = target_scale[..., 1]
        if y.ndim > center.ndim:  # multiple batches -> expand size
            center = center.view(*center.size(), *(1,) * (y.ndim - center.ndim))
            scale = scale.view(*scale.size(), *(1,) * (y.ndim - scale.ndim))

        # transform
        y = (y - center) / scale

        # return with center and scale or without
        if return_norm:
            return y, target_scale
        else:
            return y