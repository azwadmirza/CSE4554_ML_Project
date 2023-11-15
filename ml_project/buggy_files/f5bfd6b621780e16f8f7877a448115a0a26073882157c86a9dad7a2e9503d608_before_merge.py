def build(preprocessor_step_config):
  """Builds preprocessing step based on the configuration.

  Args:
    preprocessor_step_config: PreprocessingStep configuration proto.

  Returns:
    function, argmap: A callable function and an argument map to call function
                      with.

  Raises:
    ValueError: On invalid configuration.
  """
  step_type = preprocessor_step_config.WhichOneof('preprocessing_step')

  if step_type in PREPROCESSING_FUNCTION_MAP:
    preprocessing_function = PREPROCESSING_FUNCTION_MAP[step_type]
    step_config = _get_step_config_from_proto(preprocessor_step_config,
                                              step_type)
    function_args = _get_dict_from_proto(step_config)
    return (preprocessing_function, function_args)

  if step_type == 'random_horizontal_flip':
    config = preprocessor_step_config.random_horizontal_flip
    return (preprocessor.random_horizontal_flip,
            {
                'keypoint_flip_permutation': tuple(
                    config.keypoint_flip_permutation),
            })

  if step_type == 'random_vertical_flip':
    config = preprocessor_step_config.random_vertical_flip
    return (preprocessor.random_vertical_flip,
            {
                'keypoint_flip_permutation': tuple(
                    config.keypoint_flip_permutation),
            })

  if step_type == 'random_rotation90':
    return (preprocessor.random_rotation90, {})

  if step_type == 'random_crop_image':
    config = preprocessor_step_config.random_crop_image
    return (preprocessor.random_crop_image,
            {
                'min_object_covered': config.min_object_covered,
                'aspect_ratio_range': (config.min_aspect_ratio,
                                       config.max_aspect_ratio),
                'area_range': (config.min_area, config.max_area),
                'overlap_thresh': config.overlap_thresh,
                'random_coef': config.random_coef,
            })

  if step_type == 'random_pad_image':
    config = preprocessor_step_config.random_pad_image
    min_image_size = None
    if (config.HasField('min_image_height') !=
        config.HasField('min_image_width')):
      raise ValueError('min_image_height and min_image_width should be either '
                       'both set or both unset.')
    if config.HasField('min_image_height'):
      min_image_size = (config.min_image_height, config.min_image_width)

    max_image_size = None
    if (config.HasField('max_image_height') !=
        config.HasField('max_image_width')):
      raise ValueError('max_image_height and max_image_width should be either '
                       'both set or both unset.')
    if config.HasField('max_image_height'):
      max_image_size = (config.max_image_height, config.max_image_width)

    pad_color = config.pad_color
    if pad_color and len(pad_color) != 3:
      raise ValueError('pad_color should have 3 elements (RGB) if set!')
    if not pad_color:
      pad_color = None
    return (preprocessor.random_pad_image,
            {
                'min_image_size': min_image_size,
                'max_image_size': max_image_size,
                'pad_color': pad_color,
            })

  if step_type == 'random_crop_pad_image':
    config = preprocessor_step_config.random_crop_pad_image
    min_padded_size_ratio = config.min_padded_size_ratio
    if min_padded_size_ratio and len(min_padded_size_ratio) != 2:
      raise ValueError('min_padded_size_ratio should have 3 elements if set!')
    max_padded_size_ratio = config.max_padded_size_ratio
    if max_padded_size_ratio and len(max_padded_size_ratio) != 2:
      raise ValueError('max_padded_size_ratio should have 3 elements if set!')
    pad_color = config.pad_color
    if pad_color and len(pad_color) != 3:
      raise ValueError('pad_color should have 3 elements if set!')
    return (preprocessor.random_crop_pad_image,
            {
                'min_object_covered': config.min_object_covered,
                'aspect_ratio_range': (config.min_aspect_ratio,
                                       config.max_aspect_ratio),
                'area_range': (config.min_area, config.max_area),
                'overlap_thresh': config.overlap_thresh,
                'random_coef': config.random_coef,
                'min_padded_size_ratio': (min_padded_size_ratio if
                                          min_padded_size_ratio else None),
                'max_padded_size_ratio': (max_padded_size_ratio if
                                          max_padded_size_ratio else None),
                'pad_color': (pad_color if pad_color else None),
            })

  if step_type == 'random_resize_method':
    config = preprocessor_step_config.random_resize_method
    return (preprocessor.random_resize_method,
            {
                'target_size': [config.target_height, config.target_width],
            })

  if step_type == 'resize_image':
    config = preprocessor_step_config.resize_image
    method = RESIZE_METHOD_MAP[config.method]
    return (preprocessor.resize_image,
            {
                'new_height': config.new_height,
                'new_width': config.new_width,
                'method': method
            })

  if step_type == 'ssd_random_crop':
    config = preprocessor_step_config.ssd_random_crop
    if config.operations:
      min_object_covered = [op.min_object_covered for op in config.operations]
      aspect_ratio_range = [(op.min_aspect_ratio, op.max_aspect_ratio)
                            for op in config.operations]
      area_range = [(op.min_area, op.max_area) for op in config.operations]
      overlap_thresh = [op.overlap_thresh for op in config.operations]
      random_coef = [op.random_coef for op in config.operations]
      return (preprocessor.ssd_random_crop,
              {
                  'min_object_covered': min_object_covered,
                  'aspect_ratio_range': aspect_ratio_range,
                  'area_range': area_range,
                  'overlap_thresh': overlap_thresh,
                  'random_coef': random_coef,
              })
    return (preprocessor.ssd_random_crop, {})

  if step_type == 'ssd_random_crop_pad':
    config = preprocessor_step_config.ssd_random_crop_pad
    if config.operations:
      min_object_covered = [op.min_object_covered for op in config.operations]
      aspect_ratio_range = [(op.min_aspect_ratio, op.max_aspect_ratio)
                            for op in config.operations]
      area_range = [(op.min_area, op.max_area) for op in config.operations]
      overlap_thresh = [op.overlap_thresh for op in config.operations]
      random_coef = [op.random_coef for op in config.operations]
      min_padded_size_ratio = [
          (op.min_padded_size_ratio[0], op.min_padded_size_ratio[1])
          for op in config.operations]
      max_padded_size_ratio = [
          (op.max_padded_size_ratio[0], op.max_padded_size_ratio[1])
          for op in config.operations]
      pad_color = [(op.pad_color_r, op.pad_color_g, op.pad_color_b)
                   for op in config.operations]
      return (preprocessor.ssd_random_crop_pad,
              {
                  'min_object_covered': min_object_covered,
                  'aspect_ratio_range': aspect_ratio_range,
                  'area_range': area_range,
                  'overlap_thresh': overlap_thresh,
                  'random_coef': random_coef,
                  'min_padded_size_ratio': min_padded_size_ratio,
                  'max_padded_size_ratio': max_padded_size_ratio,
                  'pad_color': pad_color,
              })
    return (preprocessor.ssd_random_crop_pad, {})

  if step_type == 'ssd_random_crop_fixed_aspect_ratio':
    config = preprocessor_step_config.ssd_random_crop_fixed_aspect_ratio
    if config.operations:
      min_object_covered = [op.min_object_covered for op in config.operations]
      area_range = [(op.min_area, op.max_area) for op in config.operations]
      overlap_thresh = [op.overlap_thresh for op in config.operations]
      random_coef = [op.random_coef for op in config.operations]
      return (preprocessor.ssd_random_crop_fixed_aspect_ratio,
              {
                  'min_object_covered': min_object_covered,
                  'aspect_ratio': config.aspect_ratio,
                  'area_range': area_range,
                  'overlap_thresh': overlap_thresh,
                  'random_coef': random_coef,
              })
    return (preprocessor.ssd_random_crop_fixed_aspect_ratio, {})

  if step_type == 'ssd_random_crop_pad_fixed_aspect_ratio':
    config = preprocessor_step_config.ssd_random_crop_pad_fixed_aspect_ratio
    if config.operations:
      min_object_covered = [op.min_object_covered for op in config.operations]
      aspect_ratio_range = [(op.min_aspect_ratio, op.max_aspect_ratio)
                            for op in config.operations]
      area_range = [(op.min_area, op.max_area) for op in config.operations]
      overlap_thresh = [op.overlap_thresh for op in config.operations]
      random_coef = [op.random_coef for op in config.operations]
      min_padded_size_ratio = [
          (op.min_padded_size_ratio[0], op.min_padded_size_ratio[1])
          for op in config.operations]
      max_padded_size_ratio = [
          (op.max_padded_size_ratio[0], op.max_padded_size_ratio[1])
          for op in config.operations]
      return (preprocessor.ssd_random_crop_pad_fixed_aspect_ratio,
              {
                  'min_object_covered': min_object_covered,
                  'aspect_ratio': config.aspect_ratio,
                  'aspect_ratio_range': aspect_ratio_range,
                  'area_range': area_range,
                  'overlap_thresh': overlap_thresh,
                  'random_coef': random_coef,
                  'min_padded_size_ratio': min_padded_size_ratio,
                  'max_padded_size_ratio': max_padded_size_ratio,
              })
    return (preprocessor.ssd_random_crop_pad_fixed_aspect_ratio, {})

  raise ValueError('Unknown preprocessing step.')