    def collater(self, samples):
        samples = self.dataset.collater(samples)

        if self.new_src_eos is not None:
            if self.dataset.left_pad_source:
                assert(samples['net_input']['src_tokens'][:, -1] != self.src_eos).sum() == 0
                samples['net_input']['src_tokens'][:, -1] = self.new_src_eos
            else:
                eos_idx = samples['net_input']['src_lengths'] - 1
                assert(
                    samples['net_input']['src_tokens'][torch.arange(eos_idx.size(0)), eos_idx] != self.src_eos
                ).sum() == 0
                eos_idx = eos_idx.resize_(len(samples['net_input']['src_lengths']), 1)
                samples['net_input']['src_tokens'].scatter_(1, eos_idx, self.new_src_eos)

        if self.new_tgt_bos is not None and 'prev_output_tokens' in samples['net_input']:
            if self.dataset.left_pad_target:
                # TODO: support different padding direction on target side
                raise NotImplementedError(
                    'TransformEosLangPairDataset does not implement --left-pad-target True option'
                )
            else:
                assert (samples['net_input']['prev_output_tokens'][:, 0] != self.tgt_bos).sum() == 0
                samples['net_input']['prev_output_tokens'][:, 0] = self.new_tgt_bos

        return samples