def persistence_images(diagrams, sampling, step_size, weights, sigma):
    persistence_images_ = np.zeros(
        (diagrams.shape[0], sampling.shape[0], sampling.shape[0]))
    # Transform diagrams from (birth, death, dim) to (birth, persistence, dim)
    diagrams[:, :, 1] = diagrams[:, :, 1] - diagrams[:, :, 0]

    for axis in [0, 1]:
        # Set the values outside of the sampling range to the sampling range.
        diagrams[:, :, axis][diagrams[:, :, axis] < sampling[0, axis]] = \
            sampling[0, axis]
        diagrams[:, :, axis][diagrams[:, :, axis] > sampling[-1, axis]] = \
            sampling[-1, axis]
        # Convert into pixel
        diagrams[:, :, axis] = np.array(
            (diagrams[:, :, axis] - sampling[0, axis]) / step_size[axis],
            dtype=int)
    # Sample the image
    [_sample_image(persistence_images_[i], sampled_diag)
     for i, sampled_diag in enumerate(diagrams)]

    # Apply the weights
    persistence_images_ *= weights / np.max(weights)

    # Smoothen the weighted-image
    for i, image in enumerate(persistence_images_):
        persistence_images_[i] = gaussian_filter(image, sigma, mode="reflect")

    persistence_images_ = np.rot90(persistence_images_, k=1, axes=(1, 2))
    return persistence_images_