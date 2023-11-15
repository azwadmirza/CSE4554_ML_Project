    def find_metadata(self, gallery, lang):
        """Search for a gallery metadata file.

        If there is an metadata file for the gallery, use that to determine
        captions and the order in which images shall be displayed in the
        gallery. You only need to list the images if a specific ordering or
        caption is required. The metadata file is YAML-formatted, with field
        names of
        #
        name:
        caption:
        order:
        #
        If a numeric order value is specified, we use that directly, otherwise
        we depend on how PyYAML returns the information - which may or may not
        be in the same order as in the file itself. Non-numeric ordering is not
        supported. If no caption is specified, then we return an empty string.
        Returns a string (l18n'd filename), list (ordering), dict (captions),
        dict (image metadata).
        """
        base_meta_path = os.path.join(gallery, "metadata.yml")
        localized_meta_path = utils.get_translation_candidate(self.site.config,
                                                              base_meta_path, lang)
        order = []
        captions = {}
        custom_metadata = {}
        used_path = ""

        if os.path.isfile(localized_meta_path):
            used_path = localized_meta_path
        elif os.path.isfile(base_meta_path):
            used_path = base_meta_path
        else:
            return "", [], {}, {}

        self.logger.debug("Using {0} for gallery {1}".format(
            used_path, gallery))
        with open(used_path, "r") as meta_file:
            if yaml is None:
                utils.req_missing(['PyYAML'], 'use metadata.yml files for galleries')
            meta = yaml.safe_load_all(meta_file)
            for img in meta:
                # load_all and safe_load_all both return None as their
                # final element, so skip it
                if not img:
                    continue
                if 'name' in img:
                    img_name = img.pop('name')
                    if 'caption' in img and img['caption']:
                        captions[img_name] = img.pop('caption')

                    if 'order' in img and img['order'] is not None:
                        order.insert(img.pop('order'), img_name)
                    else:
                        order.append(img_name)
                    custom_metadata[img_name] = img
                else:
                    self.logger.error("no 'name:' for ({0}) in {1}".format(
                        img, used_path))
        return used_path, order, captions, custom_metadata