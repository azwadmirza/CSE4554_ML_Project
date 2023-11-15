    def reduce_across_time(cls, time_outputs):
        # auto-reduce across time for tbptt
        meta = time_outputs[0]['meta']

        # in 1.0 the results have 'extra'. Once we deprecate 0.10.0 we may not need this
        if 'extra' in time_outputs[0]:
            [x.pop('extra', None) for x in time_outputs]

        result = cls()
        result = recursive_gather(time_outputs, result)
        recursive_stack(result)

        for k, value in result.items():
            if k in ['meta', 'extra'] or isinstance(value, Metric):
                continue

            # pick the reduce fx
            if k in ['checkpoint_on', 'early_stop_on', 'minimize']:
                tbptt_reduce_fx = torch.mean
            else:
                tbptt_reduce_fx = meta[k]['tbptt_reduce_fx']

            if isinstance(value, dict):
                # TODO: recursive reduce:
                _recursive_fx_apply(value, tbptt_reduce_fx)
            else:
                result[k] = tbptt_reduce_fx(value.float())

        result['meta'] = meta
        return result