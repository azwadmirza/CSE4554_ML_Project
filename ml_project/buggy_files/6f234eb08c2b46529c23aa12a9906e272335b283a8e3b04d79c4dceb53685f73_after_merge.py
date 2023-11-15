def persistence_images(diagrams, sampling, step_size, sigma, weights):
    # For persistence images, `sampling` is a tall matrix with two columns
    # (the first for birth and the second for persistence), and `step_size` is
    # a 2d array
    # WARNING: modifies `diagrams` in place
    persistence_images_ = \
        np.zeros((len(diagrams), len(sampling), len(sampling)), dtype=float)
    # If both step sizes are zero, we return a trivial image
    if (step_size == 0).all():
        return persistence_images_

    # Transform diagrams from (birth, death, dim) to (birth, persistence, dim)
    diagrams[:, :, 1] -= diagrams[:, :, 0]

    sigma_pixel = []
    first_samplings = sampling[0]
    last_samplings = sampling[-1]
    for ax in [0, 1]:
        diagrams_ax = diagrams[:, :, ax]
        # Set the values outside of the sampling range
        diagrams_ax[diagrams_ax < first_samplings[ax]] = first_samplings[ax]
        diagrams_ax[diagrams_ax > last_samplings[ax]] = last_samplings[ax]
        # Calculate the value of the component of `sigma` in pixel units
        sigma_pixel.append(sigma / step_size[ax])

    # Sample the image, apply the weights, smoothen
    for i, diagram in enumerate(diagrams):
        nontrivial_points_idx = np.flatnonzero(diagram[:, 1])
        diagram_nontrivial_pixel_coords = np.array(
            (diagram - first_samplings) / step_size, dtype=int
        )[nontrivial_points_idx]
        image = persistence_images_[i]
        _sample_image(image, diagram_nontrivial_pixel_coords)
        image *= weights
        gaussian_filter(image, sigma_pixel, mode="constant", output=image)

    persistence_images_ = np.rot90(persistence_images_, k=1, axes=(1, 2))
    persistence_images_ /= np.product(step_size)
    return persistence_images_