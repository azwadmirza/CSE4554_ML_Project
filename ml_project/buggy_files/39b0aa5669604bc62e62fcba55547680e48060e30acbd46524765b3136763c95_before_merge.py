    def visit_image(self, node: Element) -> None:
        olduri = node['uri']
        # rewrite the URI if the environment knows about it
        if olduri in self.builder.images:
            node['uri'] = posixpath.join(self.builder.imgpath,
                                         self.builder.images[olduri])

        if 'scale' in node:
            # Try to figure out image height and width.  Docutils does that too,
            # but it tries the final file name, which does not necessarily exist
            # yet at the time the HTML file is written.
            if not ('width' in node and 'height' in node):
                size = get_image_size(os.path.join(self.builder.srcdir, olduri))
                if size is None:
                    logger.warning(__('Could not obtain image size. :scale: option is ignored.'),  # NOQA
                                   location=node)
                else:
                    if 'width' not in node:
                        node['width'] = str(size[0])
                    if 'height' not in node:
                        node['height'] = str(size[1])

        uri = node['uri']
        if uri.lower().endswith(('svg', 'svgz')):
            atts = {'src': uri}
            if 'width' in node:
                atts['width'] = node['width']
            if 'height' in node:
                atts['height'] = node['height']
            if 'scale' in node:
                scale = node['scale'] / 100.0
                if 'width' in atts:
                    atts['width'] = int(atts['width']) * scale
                if 'height' in atts:
                    atts['height'] = int(atts['height']) * scale
            atts['alt'] = node.get('alt', uri)
            if 'align' in node:
                atts['class'] = 'align-%s' % node['align']
            self.body.append(self.emptytag(node, 'img', '', **atts))
            return

        super().visit_image(node)