def get_enhanced_image(dataset,
                       enhancer=None,
                       fill_value=None,
                       ppp_config_dir=None,
                       enhancement_config_file=None,
                       overlay=None,
                       decorate=None):
    mode = _determine_mode(dataset)
    if ppp_config_dir is None:
        ppp_config_dir = get_environ_config_dir()

    if enhancer is None:
        enhancer = Enhancer(ppp_config_dir, enhancement_config_file)

    if enhancer.enhancement_tree is None:
        raise RuntimeError(
            "No enhancement configuration files found or specified, cannot"
            " automatically enhance dataset")

    if dataset.info.get("sensor", None):
        enhancer.add_sensor_enhancements(dataset.info["sensor"])

    # Create an image for enhancement
    img = to_image(dataset, mode=mode, fill_value=fill_value)
    enhancer.apply(img, **dataset.info)

    img.info.update(dataset.info)

    if overlay is not None:
        add_overlay(img, dataset.info['area'], **overlay)

    if decorate is not None:
        add_decorate(img, **decorate)

    return img