def _execute_compiled_primitive(prim, compiled, backend, result_handler, *args):
  device_num, = compiled.DeviceOrdinals()
  input_bufs = [device_put(x, device_num, backend=backend) for x in args]
  out_buf = compiled.Execute(input_bufs)
  if FLAGS.jax_debug_nans:
    check_nans(prim, out_buf.destructure() if prim.multiple_results else out_buf)
  return result_handler(out_buf)