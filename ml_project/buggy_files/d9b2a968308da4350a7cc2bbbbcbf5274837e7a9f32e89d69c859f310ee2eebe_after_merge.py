def random_affine_generator(
    batch_size: int,
    height: int,
    width: int,
    degrees: torch.Tensor,
    translate: Optional[torch.Tensor] = None,
    scale: Optional[torch.Tensor] = None,
    shear: Optional[torch.Tensor] = None,
    same_on_batch: bool = False,
) -> Dict[str, torch.Tensor]:
    r"""Get parameters for ``affine`` for a random affine transform.

    Args:
        batch_size (int): the tensor batch size.
        height (int) : height of the image.
        width (int): width of the image.
        degrees (tensor): Range of degrees to select from like (min, max).
        translate (tensor, optional): tuple of maximum absolute fraction for horizontal
            and vertical translations. For example translate=(a, b), then horizontal shift
            is randomly sampled in the range -img_width * a < dx < img_width * a and vertical shift is
            randomly sampled in the range -img_height * b < dy < img_height * b. Will not translate by default.
        scale (tensor, optional): scaling factor interval, e.g (a, b), then scale is
            randomly sampled from the range a <= scale <= b. Will keep original scale by default.
        shear (tensor, optional): Range of degrees to select from.
            Shear is a 2x2 tensor, a x-axis shear in (shear[0][0], shear[0][1]) and y-axis shear in
            (shear[1][0], shear[1][1]) will be applied. Will not apply shear by default.
        same_on_batch (bool): apply the same transformation across the batch. Default: False.

    Returns:
        params Dict[str, torch.Tensor]: parameters to be passed for transformation.
    """
    _common_param_check(batch_size, same_on_batch)
    _joint_range_check(degrees, "degrees")
    assert isinstance(width, (int,)) and isinstance(height, (int,)) and width > 0 and height > 0, \
        f"`width` and `height` must be positive integers. Got {width}, {height}."

    device, dtype = _extract_device_dtype([degrees, translate, scale, shear])
    angle = _adapted_uniform((batch_size,), degrees[0], degrees[1], same_on_batch)

    # compute tensor ranges
    if scale is not None:
        _joint_range_check(cast(torch.Tensor, scale[:2]), "scale")
        _scale = _adapted_uniform((batch_size,), scale[0], scale[1], same_on_batch).unsqueeze(1).repeat(1, 2)
        if len(scale) == 4:
            _joint_range_check(cast(torch.Tensor, scale[2:]), "scale_y")
            _scale[:, 1] = _adapted_uniform((batch_size,), scale[2], scale[3], same_on_batch)
    else:
        _scale = torch.ones((batch_size, 2), device=device, dtype=dtype)

    if translate is not None:
        _joint_range_check(cast(torch.Tensor, translate), "translate")
        max_dx: torch.Tensor = translate[0] * width
        max_dy: torch.Tensor = translate[1] * height
        translations = torch.stack([
            _adapted_uniform((batch_size,), -max_dx, max_dx, same_on_batch),
            _adapted_uniform((batch_size,), -max_dy, max_dy, same_on_batch)
        ], dim=-1)
    else:
        translations = torch.zeros((batch_size, 2), device=device, dtype=dtype)

    center: torch.Tensor = torch.tensor(
        [width, height], device=device, dtype=dtype).view(1, 2) / 2. - 0.5
    center = center.expand(batch_size, -1)

    if shear is not None:
        _joint_range_check(cast(torch.Tensor, shear)[0], "shear")
        _joint_range_check(cast(torch.Tensor, shear)[1], "shear")
        sx = _adapted_uniform((batch_size,), shear[0][0], shear[0][1], same_on_batch)
        sy = _adapted_uniform((batch_size,), shear[1][0], shear[1][1], same_on_batch)
    else:
        sx = sy = torch.tensor([0] * batch_size)

    return dict(translations=translations,
                center=center,
                scale=_scale,
                angle=angle,
                sx=sx,
                sy=sy)