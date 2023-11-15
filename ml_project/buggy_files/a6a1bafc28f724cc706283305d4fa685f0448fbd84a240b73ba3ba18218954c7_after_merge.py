    def confidence_region(self):
        """
        Returns 2 standard deviations above and below the mean.

        :rtype: (torch.Tensor, torch.Tensor)
        :return: pair of tensors of size (b x d) or (d), where
            b is the batch size and d is the dimensionality of the random
            variable. The first (second) Tensor is the lower (upper) end of
            the confidence region.
        """
        std2 = self.stddev.mul_(2)
        mean = self.mean
        return mean.sub(std2), mean.add(std2)