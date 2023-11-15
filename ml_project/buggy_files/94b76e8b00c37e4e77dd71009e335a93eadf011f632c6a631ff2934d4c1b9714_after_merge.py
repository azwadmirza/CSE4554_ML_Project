    def render_gallery_index(
            self,
            template_name,
            output_name,
            context,
            img_list,
            img_titles,
            thumbs,
            file_dep):
        """Build the gallery index."""
        # The photo array needs to be created here, because
        # it relies on thumbnails already being created on
        # output

        def url_from_path(p):
            url = '/'.join(os.path.relpath(p, os.path.dirname(output_name) + os.sep).split(os.sep))
            return url

        photo_array = []
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
            photo_array.append({
                'url': url_from_path(img),
                'url_thumb': url_from_path(thumb),
                'title': title,
                'size': {
                    'w': w,
                    'h': h
                },
            })
        context['photo_array'] = photo_array
        context['photo_array_json'] = json.dumps(photo_array, sort_keys=True)
        self.site.render_template(template_name, output_name, context)