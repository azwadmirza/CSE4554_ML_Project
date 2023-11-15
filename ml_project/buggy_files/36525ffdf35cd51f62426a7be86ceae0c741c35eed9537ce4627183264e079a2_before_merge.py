        def make_one_hot(batch, depth=2):
            """
            Creates a one-hot embedding of dimension 2.
            Parameters:
            batch: list of size batch_size of class predictions
            Returns:
            one hot encoding of size [batch_size, 2]
            """
            ones = torch.sparse.torch.eye(depth).cuda()
            return ones.index_select(0, batch)