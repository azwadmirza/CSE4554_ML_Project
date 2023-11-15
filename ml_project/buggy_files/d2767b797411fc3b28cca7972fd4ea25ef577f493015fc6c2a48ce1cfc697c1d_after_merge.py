def resample_waveform(waveform: Tensor,
                      orig_freq: float,
                      new_freq: float,
                      lowpass_filter_width: int = 6) -> Tensor:
    r"""Resamples the waveform at the new frequency. This matches Kaldi's OfflineFeatureTpl ResampleWaveform
    which uses a LinearResample (resample a signal at linearly spaced intervals to upsample/downsample
    a signal). LinearResample (LR) means that the output signal is at linearly spaced intervals (i.e
    the output signal has a frequency of ``new_freq``). It uses sinc/bandlimited interpolation to
    upsample/downsample the signal.

    https://ccrma.stanford.edu/~jos/resample/Theory_Ideal_Bandlimited_Interpolation.html
    https://github.com/kaldi-asr/kaldi/blob/master/src/feat/resample.h#L56

    Args:
        waveform (Tensor): The input signal of size (c, n)
        orig_freq (float): The original frequency of the signal
        new_freq (float): The desired frequency
        lowpass_filter_width (int, optional): Controls the sharpness of the filter, more == sharper
            but less efficient. We suggest around 4 to 10 for normal use. (Default: ``6``)

    Returns:
        Tensor: The waveform at the new frequency
    """
    device, dtype = waveform.device, waveform.dtype

    assert waveform.dim() == 2
    assert orig_freq > 0.0 and new_freq > 0.0

    min_freq = min(orig_freq, new_freq)
    lowpass_cutoff = 0.99 * 0.5 * min_freq

    assert lowpass_cutoff * 2 <= min_freq

    base_freq = math.gcd(int(orig_freq), int(new_freq))
    input_samples_in_unit = int(orig_freq) // base_freq
    output_samples_in_unit = int(new_freq) // base_freq

    window_width = lowpass_filter_width / (2.0 * lowpass_cutoff)
    first_indices, weights = _get_LR_indices_and_weights(
        orig_freq, new_freq, output_samples_in_unit,
        window_width, lowpass_cutoff, lowpass_filter_width, device, dtype)

    assert first_indices.dim() == 1
    # TODO figure a better way to do this. conv1d reaches every element i*stride + padding
    # all the weights have the same stride but have different padding.
    # Current implementation takes the input and applies the various padding before
    # doing a conv1d for that specific weight.
    conv_stride = input_samples_in_unit
    conv_transpose_stride = output_samples_in_unit
    num_channels, wave_len = waveform.size()
    window_size = weights.size(1)
    tot_output_samp = _get_num_LR_output_samples(wave_len, orig_freq, new_freq)
    output = torch.zeros((num_channels, tot_output_samp),
                         device=device, dtype=dtype)
    # eye size: (num_channels, num_channels, 1)
    eye = torch.eye(num_channels, device=device, dtype=dtype).unsqueeze(2)
    for i in range(first_indices.size(0)):
        wave_to_conv = waveform
        first_index = int(first_indices[i].item())
        if first_index >= 0:
            # trim the signal as the filter will not be applied before the first_index
            wave_to_conv = wave_to_conv[..., first_index:]

        # pad the right of the signal to allow partial convolutions meaning compute
        # values for partial windows (e.g. end of the window is outside the signal length)
        max_unit_index = (tot_output_samp - 1) // output_samples_in_unit
        end_index_of_last_window = max_unit_index * conv_stride + window_size
        current_wave_len = wave_len - first_index
        right_padding = max(0, end_index_of_last_window + 1 - current_wave_len)

        left_padding = max(0, -first_index)
        if left_padding != 0 or right_padding != 0:
            wave_to_conv = torch.nn.functional.pad(wave_to_conv, (left_padding, right_padding))

        conv_wave = torch.nn.functional.conv1d(
            wave_to_conv.unsqueeze(0), weights[i].repeat(num_channels, 1, 1),
            stride=conv_stride, groups=num_channels)

        # we want conv_wave[:, i] to be at output[:, i + n*conv_transpose_stride]
        dilated_conv_wave = torch.nn.functional.conv_transpose1d(
            conv_wave, eye, stride=conv_transpose_stride).squeeze(0)

        # pad dilated_conv_wave so it reaches the output length if needed.
        dialated_conv_wave_len = dilated_conv_wave.size(-1)
        left_padding = i
        right_padding = max(0, tot_output_samp - (left_padding + dialated_conv_wave_len))
        dilated_conv_wave = torch.nn.functional.pad(
            dilated_conv_wave, (left_padding, right_padding))[..., :tot_output_samp]

        output += dilated_conv_wave

    return output