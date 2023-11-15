    def collater(self, samples):
        samples = self.dataset.collater(samples)

        # TODO: support different padding direction
        if self.new_src_eos is not None:
            assert(samples['net_input']['src_tokens'][:, -1] != self.src_eos).sum() == 0
            samples['net_input']['src_tokens'][:, -1] = self.new_src_eos

        if self.new_tgt_bos is not None:
            assert (samples['net_input']['prev_output_tokens'][:, 0] != self.tgt_bos).sum() == 0
            samples['net_input']['prev_output_tokens'][:, 0] = self.new_tgt_bos

        return samples