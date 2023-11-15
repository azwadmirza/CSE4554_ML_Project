def _get_LR_indices_and_weights(orig_freq: float,
                                new_freq: float,
                                output_samples_in_unit: int,
                                window_width: float,
                                lowpass_cutoff: float,
                                lowpass_filter_width: int) -> Tuple[Tensor, Tensor]:
    r"""Based on LinearResample::SetIndexesAndWeights where it retrieves the weights for
    resampling as well as the indices in which they are valid. LinearResample (LR) means
    that the output signal is at linearly spaced intervals (i.e the output signal has a
    frequency of ``new_freq``). It uses sinc/bandlimited interpolation to upsample/downsample
    the signal.

    The reason why the same filter is not used for multiple convolutions is because the
    sinc function could sampled at different points in time. For example, suppose
    a signal is sampled at the timestamps (seconds)
    0         16        32
    and we want it to be sampled at the timestamps (seconds)
    0 5 10 15   20 25 30  35
    at the timestamp of 16, the delta timestamps are
    16 11 6 1   4  9  14  19
    at the timestamp of 32, the delta timestamps are
    32 27 22 17 12 8 2    3

    As we can see from deltas, the sinc function is sampled at different points of time
    assuming the center of the sinc function is at 0, 16, and 32 (the deltas [..., 6, 1, 4, ....]
    for 16 vs [...., 2, 3, ....] for 32)

    Example, one case is when the ``orig_freq`` and ``new_freq`` are multiples of each other then
    there needs to be one filter.

    A windowed filter function (i.e. Hanning * sinc) because the ideal case of sinc function
    has infinite support (non-zero for all values) so instead it is truncated and multiplied by
    a window function which gives it less-than-perfect rolloff [1].

    [1] Chapter 16: Windowed-Sinc Filters, https://www.dspguide.com/ch16/1.htm

    Args:
        orig_freq (float): The original frequency of the signal
        new_freq (float): The desired frequency
        output_samples_in_unit (int): The number of output samples in the smallest repeating unit:
            num_samp_out = new_freq / Gcd(orig_freq, new_freq)
        window_width (float): The width of the window which is nonzero
        lowpass_cutoff (float): The filter cutoff in Hz. The filter cutoff needs to be less
            than samp_rate_in_hz/2 and less than samp_rate_out_hz/2.
        lowpass_filter_width (int): Controls the sharpness of the filter, more == sharper but less
            efficient. We suggest around 4 to 10 for normal use

    Returns:
        (Tensor, Tensor): A tuple of ``min_input_index`` (which is the minimum indices
        where the window is valid, size (``output_samples_in_unit``)) and ``weights`` (which is the weights
        which correspond with min_input_index, size (``output_samples_in_unit``, ``max_weight_width``)).
    """
    assert lowpass_cutoff < min(orig_freq, new_freq) / 2
    output_t = torch.arange(0., output_samples_in_unit) / new_freq
    min_t = output_t - window_width
    max_t = output_t + window_width

    min_input_index = torch.ceil(min_t * orig_freq)  # size (output_samples_in_unit)
    max_input_index = torch.floor(max_t * orig_freq)  # size (output_samples_in_unit)
    num_indices = max_input_index - min_input_index + 1  # size (output_samples_in_unit)

    max_weight_width = num_indices.max()
    # create a group of weights of size (output_samples_in_unit, max_weight_width)
    j = torch.arange(max_weight_width).unsqueeze(0)
    input_index = min_input_index.unsqueeze(1) + j
    delta_t = (input_index / orig_freq) - output_t.unsqueeze(1)

    weights = torch.zeros_like(delta_t)
    inside_window_indices = delta_t.abs().lt(window_width)
    # raised-cosine (Hanning) window with width `window_width`
    weights[inside_window_indices] = 0.5 * (1 + torch.cos(2 * math.pi * lowpass_cutoff /
                                                          lowpass_filter_width * delta_t[inside_window_indices]))

    t_eq_zero_indices = delta_t.eq(0.0)
    t_not_eq_zero_indices = ~t_eq_zero_indices
    # sinc filter function
    weights[t_not_eq_zero_indices] *= torch.sin(
        2 * math.pi * lowpass_cutoff * delta_t[t_not_eq_zero_indices]) / (math.pi * delta_t[t_not_eq_zero_indices])
    # limit of the function at t = 0
    weights[t_eq_zero_indices] *= 2 * lowpass_cutoff

    weights /= orig_freq  # size (output_samples_in_unit, max_weight_width)
    return min_input_index, weights