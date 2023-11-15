    def forward(self, hs_pad, hlens, ys_pad):
        """CTC forward

        :param torch.Tensor hs_pad: batch of padded hidden state sequences (B, Tmax, D)
        :param torch.Tensor hlens: batch of lengths of hidden state sequences (B)
        :param torch.Tensor ys_pad: batch of padded character id sequence tensor (B, Lmax)
        :return: ctc loss value
        :rtype: torch.Tensor
        """
        # TODO(kan-bayashi): need to make more smart way
        ys = [y[y != self.ignore_id] for y in ys_pad]  # parse padded ys

        self.loss = None
        hlens = torch.from_numpy(np.fromiter(hlens, dtype=np.int32))
        olens = torch.from_numpy(np.fromiter(
            (x.size(0) for x in ys), dtype=np.int32))

        # zero padding for hs
        ys_hat = self.ctc_lo(F.dropout(hs_pad, p=self.dropout_rate))

        # zero padding for ys
        ys_true = torch.cat(ys).cpu().int()  # batch x olen

        # get length info
        logging.info(self.__class__.__name__ + ' input lengths:  ' + ''.join(str(hlens).split('\n')))
        logging.info(self.__class__.__name__ + ' output lengths: ' + ''.join(str(olens).split('\n')))

        # get ctc loss
        # expected shape of seqLength x batchSize x alphabet_size
        dtype = ys_hat.dtype
        ys_hat = ys_hat.transpose(0, 1)
        if self.ctc_type == "warpctc" or dtype == torch.float16:
            # warpctc only supports float32
            # torch.ctc does not support float16 (#1751)
            ys_hat = ys_hat.to(dtype=torch.float32)
        if self.ctc_type == "builtin":
            # use GPU when using the cuDNN implementation
            ys_true = to_device(self, ys_true)
        self.loss = to_device(self, self.loss_fn(ys_hat, ys_true, hlens, olens)).to(dtype=dtype)
        if self.reduce:
            # NOTE: sum() is needed to keep consistency since warpctc return as tensor w/ shape (1,)
            # but builtin return as tensor w/o shape (scalar).
            self.loss = self.loss.sum()
            logging.info('ctc loss:' + str(float(self.loss)))

        return self.loss