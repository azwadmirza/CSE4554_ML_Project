    def render_gallery_index(
            self,
            template_name,
            output_name,
            context,
            img_list,
            img_titles,
            thumbs,
            img_metadata):
        """Build the gallery index."""
        # The photo array needs to be created here, because
        # it relies on thumbnails already being created on
        # output

        def url_from_path(p):
            url = '/'.join(os.path.relpath(p, os.path.dirname(output_name) + os.sep).split(os.sep))
            return url

        all_data = list(zip(img_list, thumbs, img_titles))

        if self.kw['sort_by_date']:
            all_data.sort(key=lambda a: self.image_date(a[0]))
        else:  # Sort by name
            all_data.sort(key=lambda a: a[0])

        if all_data:
            img_list, thumbs, img_titles = zip(*all_data)
        else:
            img_list, thumbs, img_titles = [], [], []

        photo_info = {}
        for img, thumb, title in zip(img_list, thumbs, img_titles):
            w, h = _image_size_cache.get(thumb, (None, None))
            if w is None:
                if os.path.splitext(thumb)[1] in ['.svg', '.svgz']:
                    w, h = 200, 200
                else:
                    im = Image.open(thumb)
                    w, h = im.size
                    _image_size_cache[thumb] = w, h
            # Thumbs are files in output, we need URLs
            url = url_from_path(img)
            photo_info[url] = {
                'url': url,
                'url_thumb': url_from_path(thumb),
                'title': title,
                'size': {
                    'w': w,
                    'h': h
                },
                'width': w,
                'height': h
            }
            if url in img_metadata:
                photo_info[url].update(img_metadata[url])
        photo_array = []
        if context['order']:
            for entry in context['order']:
                photo_array.append(photo_info.pop(entry))
            # Do we have any orphan entries from metadata.yml, or
            # are the files from the gallery not listed in metadata.yml?
            if photo_info:
                for entry in photo_info:
                    photo_array.append(photo_info[entry])
        else:
            for entry in photo_info:
                photo_array.append(photo_info[entry])

        context['photo_array'] = photo_array
        context['photo_array_json'] = json.dumps(photo_array, sort_keys=True)

        self.site.render_template(template_name, output_name, context)