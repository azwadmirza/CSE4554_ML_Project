def heats(diagrams, sampling, step_size, sigma):
    # WARNING: modifies `diagrams` in place
    heats_ = \
        np.zeros((len(diagrams), len(sampling), len(sampling)), dtype=float)
    # If the step size is zero, we return a trivial image
    if step_size == 0:
        return heats_

    # Set the values outside of the sampling range
    first_sampling, last_sampling = sampling[0, 0, 0], sampling[-1, 0, 0]
    diagrams[diagrams < first_sampling] = first_sampling
    diagrams[diagrams > last_sampling] = last_sampling

    # Calculate the value of `sigma` in pixel units
    sigma_pixel = sigma / step_size

    for i, diagram in enumerate(diagrams):
        nontrivial_points_idx = np.flatnonzero(diagram[:, 1] != diagram[:, 0])
        diagram_nontrivial_pixel_coords = np.array(
            (diagram - first_sampling) / step_size, dtype=int
        )[nontrivial_points_idx]
        image = heats_[i]
        _sample_image(image, diagram_nontrivial_pixel_coords)
        gaussian_filter(image, sigma_pixel, mode="constant", output=image)

    heats_ -= np.transpose(heats_, (0, 2, 1))
    heats_ /= (step_size ** 2)
    heats_ = np.rot90(heats_, k=1, axes=(1, 2))
    return heats_