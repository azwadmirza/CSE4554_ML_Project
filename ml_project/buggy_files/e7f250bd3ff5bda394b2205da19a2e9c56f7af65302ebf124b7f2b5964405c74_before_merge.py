    def __call__(self, x, y=None, quality=None, clip_values=(0, 1)):
        """
        Apply jpeg compression to sample `x`.

        :param x: Sample to compress with shape `(batch_size, width, height, depth)`.
        :type x: `np.ndarray`
        :param y: Labels of the sample `x`. This function does not affect them in any way.
        :type y: `np.ndarray`
        :param quality: The image quality, on a scale from 1 (worst) to 95 (best). Values above 95 should be avoided.
        :type quality: `int`
        :return: compressed sample
        :rtype: `np.ndarray`
        """
        if quality is not None:
            self.set_params(quality=quality)

        assert self.channel_index < len(x.shape)

        # Swap channel index
        if self.channel_index < 3:
            x_ = np.swapaxes(x, self.channel_index, 3)
        else:
            x_ = x.copy()

        # Convert into `uint8`
        x_ = x_ * 255
        x_ = x_.astype("uint8")

        # Convert to 'L' mode
        if x_.shape[-1] == 1:
            x_ = np.reshape(x_, x_.shape[:-1])

        # Compress one image per time
        for i, xi in enumerate(x_):
            if len(xi.shape) == 2:
                xi = Image.fromarray(xi, mode='L')
            elif xi.shape[-1] == 3:
                xi = Image.fromarray(xi, mode='RGB')
            else:
                logger.log(level=40, msg="Currently only support `RGB` and `L` images.")
                raise NotImplementedError("Currently only support `RGB` and `L` images.")

            out = BytesIO()
            xi.save(out, format="jpeg", quality=self.quality)
            xi = Image.open(out)
            xi = np.array(xi)
            x_[i] = xi
            del out

        # Expand dim if black/white images
        if len(x_.shape) < 4:
            x_ = np.expand_dims(x_, 3)

        # Convert to old dtype
        x_ = x_ / 255.0
        x_ = x_.astype(NUMPY_DTYPE)

        # Swap channel index
        if self.channel_index < 3:
            x_ = np.swapaxes(x_, self.channel_index, 3)

        x_ = np.clip(x_, clip_values[0], clip_values[1])

        return x_