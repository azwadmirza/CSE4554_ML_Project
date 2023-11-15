def update_manifest(ref=None):
    """
    Given a git reference in the Noto repo, such as a git commit hash or tag, extract
    information about the fonts available for use and save that information to the
    manifest file.

    The Noto repo currently contains both an older style and the newer "Phase 3"
    fonts. Phase 3 fonts have more consistent internal metrics which makes them amenable
    to being merged together, which we make use of. The older fonts are still usable,
    but cannot be merged together.

    Noto also contains both standard and "UI" variants of many fonts. When a font has a
    UI variant, it means that some of the glyphs in the standard variant are very tall
    and might overflow a typical line of text; the UI variant has the glypsh redrawn
    to fit.

    When searching for fonts to include, we take all language fonts that have both a
    regular and a bold variant, with preference given to Phase 3 and UI variants.
    """

    # grab the head of master
    if not ref:
        logging.info("Using head of master")
        ref = _request("git/refs/heads/master")["object"]["sha"]

    logging.info("Generating new manifest for reference '{}'".format(ref))

    git_tree = _request("git/trees/{}?recursive=1".format(ref))

    # backups
    font_info = _font_info(git_tree, ref, OLD_STYLE_PATH, _old_download_url)
    # prefer phase 3, replacing old-styles when possible
    font_info.update(_font_info(git_tree, ref, PHASE_3_PATH, _p3_download_url))

    new_manifest = {KEY_REF: ref, KEY_FONTS: font_info}
    utils.json_dump_formatted(new_manifest, FONTS_SOURCE, FONT_MANIFEST_NAME)