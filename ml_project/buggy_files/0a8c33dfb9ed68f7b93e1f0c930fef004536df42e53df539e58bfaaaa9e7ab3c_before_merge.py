  def _add_quant_wrapper(layer):
    # Already annotated layer. No need to wrap.
    if isinstance(layer, quantize_annotate_mod.QuantizeAnnotate):
      return layer

    return quantize_annotate_mod.QuantizeAnnotate(layer)