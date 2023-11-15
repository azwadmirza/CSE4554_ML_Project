    def initialize_from_data(self, train_x, train_y, **kwargs):
        if not torch.is_tensor(train_x) or not torch.is_tensor(train_y):
            raise RuntimeError("train_x and train_y should be tensors")
        if train_x.ndimension() == 1:
            train_x = train_x.unsqueeze(-1)
        if train_x.ndimension() == 2:
            train_x = train_x.unsqueeze(0)

        train_x_sort = train_x.sort(1)[0]
        max_dist = train_x_sort[:, -1, :] - train_x_sort[:, 0, :]
        min_dist_sort = (train_x_sort[:, 1:, :] - train_x_sort[:, :-1, :]).squeeze(0)
        min_dist = torch.zeros(1, self.ard_num_dims)
        for ind in range(self.ard_num_dims):
            min_dist[:, ind] = min_dist_sort[(torch.nonzero(min_dist_sort[:, ind]))[0], ind]

        # Inverse of lengthscales should be drawn from truncated Gaussian | N(0, max_dist^2) |
        self.log_mixture_scales.data.normal_().mul_(max_dist).abs_().pow_(-1).log_()
        # Draw means from Unif(0, 0.5 / minimum distance between two points)
        self.log_mixture_means.data.uniform_().mul_(0.5).div_(min_dist).log_()
        # Mixture weights should be roughly the stdv of the y values divided by the number of mixtures
        self.log_mixture_weights.data.fill_(train_y.std() / self.num_mixtures).log_()