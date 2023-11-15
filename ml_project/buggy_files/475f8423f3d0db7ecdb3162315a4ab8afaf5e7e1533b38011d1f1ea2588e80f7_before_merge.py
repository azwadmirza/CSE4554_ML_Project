def pad_batch_rule(batched_args, batch_dims, padding_config):
  operand, padding_value = batched_args
  operand_bdim, padding_value_bdim = batch_dims
  if padding_value_bdim is None:
    assert operand_bdim is not None
    padding_config = list(padding_config)
    padding_config.insert(operand_bdim, (0, 0, 0))
    return pad(operand, padding_value, padding_config), operand_bdim
  else:
    raise NotImplementedError