def _determine_mode(dataset):
    if "mode" in dataset.attrs:
        return dataset.attrs["mode"]

    if dataset.ndim == 2:
        return "L"
    elif dataset.shape[0] == 2:
        return "LA"
    elif dataset.shape[0] == 3:
        return "RGB"
    elif dataset.shape[0] == 4:
        return "RGBA"
    else:
        raise RuntimeError("Can't determine 'mode' of dataset: %s" %
                           str(dataset))