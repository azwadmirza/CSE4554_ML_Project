def array_result_handler(device, aval):
  return partial(DeviceArray, raise_to_shaped(aval), device)