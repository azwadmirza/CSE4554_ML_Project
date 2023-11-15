    def load(self) -> Tuple[torch.Tensor, np.ndarray]:
        r"""Load the image from disk.

        The file is expected to be monomodal/grayscale and 2D or 3D.
        A channels dimension is added to the tensor.

        Returns:
            Tuple containing a 4D data tensor of size
            :math:`(1, D_{in}, H_{in}, W_{in})`
            and a 2D 4x4 affine matrix
        """
        if self.path is None:
            return
        tensor, affine = read_image(self.path)
        # https://github.com/pytorch/pytorch/issues/9410#issuecomment-404968513
        tensor = tensor[(None,) * (3 - tensor.ndim)]  # force to be 3D
        # Remove next line and uncomment the two following ones once/if this issue
        # gets fixed:
        # https://github.com/pytorch/pytorch/issues/29010
        # See also https://discuss.pytorch.org/t/collating-named-tensors/78650/4
        tensor = tensor.unsqueeze(0)  # add channels dimension
        # name_dimensions(tensor, affine)
        # tensor = tensor.align_to('channels', ...)
        if self.check_nans and torch.isnan(tensor).any():
            warnings.warn(f'NaNs found in file "{self.path}"')
        self[DATA] = tensor
        self[AFFINE] = affine
        self._loaded = True