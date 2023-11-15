    def update_metrics(self, logits, labels, tagmask=None):
        logits, labels = logits.detach(), labels.detach()

        def make_one_hot(batch, depth=2):
            """
            Creates a one-hot embedding of dimension 2.
            Parameters:
            batch: list of size batch_size of class predictions
            Returns:
            one hot encoding of size [batch_size, 2]
            """
            ones = torch.sparse.torch.eye(depth)
            if torch.cuda.is_available():
                ones = ones.cuda()
            return ones.index_select(0, batch)

        binary_preds = make_one_hot(logits, depth=2)
        # Make label_ints a batch_size list of labels
        label_ints = torch.argmax(labels, dim=1)
        self.f1_scorer(binary_preds, label_ints)
        self.acc_scorer(binary_preds.long(), labels.long())