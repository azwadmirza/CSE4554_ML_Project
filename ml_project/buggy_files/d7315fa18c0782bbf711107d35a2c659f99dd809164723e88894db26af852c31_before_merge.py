    def import_attachment(self, item, wordpress_namespace):
        """Import an attachment to the site."""
        # Download main image
        url = get_text_tag(
            item, '{{{0}}}attachment_url'.format(wordpress_namespace), 'foo')
        link = get_text_tag(item, '{{{0}}}link'.format(wordpress_namespace),
                            'foo')
        path = urlparse(url).path
        dst_path = os.path.join(*([self.output_folder, 'files'] + list(path.split('/'))))
        dst_dir = os.path.dirname(dst_path)
        utils.makedirs(dst_dir)
        LOGGER.info("Downloading {0} => {1}".format(url, dst_path))
        self.download_url_content_to_file(url, dst_path)
        dst_url = '/'.join(dst_path.split(os.sep)[2:])
        links[link] = '/' + dst_url
        links[url] = '/' + dst_url

        files = [path]
        files_meta = [{}]

        additional_metadata = item.findall('{{{0}}}postmeta'.format(wordpress_namespace))
        if phpserialize and additional_metadata:
            source_path = os.path.dirname(url)
            for element in additional_metadata:
                meta_key = element.find('{{{0}}}meta_key'.format(wordpress_namespace))
                if meta_key is not None and meta_key.text == '_wp_attachment_metadata':
                    meta_value = element.find('{{{0}}}meta_value'.format(wordpress_namespace))

                    if meta_value is None:
                        continue

                    # Someone from Wordpress thought it was a good idea
                    # serialize PHP objects into that metadata field. Given
                    # that the export should give you the power to insert
                    # your blogging into another site or system its not.
                    # Why don't they just use JSON?
                    if sys.version_info[0] == 2:
                        try:
                            metadata = phpserialize.loads(utils.sys_encode(meta_value.text))
                        except ValueError:
                            # local encoding might be wrong sometimes
                            metadata = phpserialize.loads(meta_value.text.encode('utf-8'))
                    else:
                        metadata = phpserialize.loads(meta_value.text.encode('utf-8'))

                    meta_key = b'image_meta'
                    size_key = b'sizes'
                    file_key = b'file'
                    width_key = b'width'
                    height_key = b'height'

                    # Extract metadata
                    if width_key in metadata and height_key in metadata:
                        files_meta[0]['width'] = int(metadata[width_key])
                        files_meta[0]['height'] = int(metadata[height_key])

                    if meta_key in metadata:
                        image_meta = metadata[meta_key]
                        dst_meta = {}

                        def add(our_key, wp_key, is_int=False, ignore_zero=False):
                            if wp_key in image_meta:
                                value = image_meta[wp_key]
                                if is_int:
                                    value = int(value)
                                    if ignore_zero and value == 0:
                                        return
                                else:
                                    value = value.decode('utf-8')  # assume UTF-8
                                    if value == '':  # skip empty values
                                        return
                                dst_meta[our_key] = value

                        add('aperture', b'aperture', is_int=True, ignore_zero=True)
                        add('credit', b'credit')
                        add('camera', b'camera')
                        add('caption', b'caption')
                        add('created_timestamp', b'created_timestamp', is_int=True, ignore_zero=True)
                        add('copyright', b'copyright')
                        add('focal_length', b'focal_length', is_int=True, ignore_zero=True)
                        add('iso', b'iso', is_int=True, ignore_zero=True)
                        add('shutter_speed', b'shutter_speed', is_int=True, ignore_zero=True)
                        add('title', b'title')

                        if len(dst_meta) > 0:
                            files_meta[0]['meta'] = dst_meta

                    # Find other sizes of image
                    if size_key not in metadata:
                        continue

                    for size in metadata[size_key]:
                        filename = metadata[size_key][size][file_key]
                        url = '/'.join([source_path, filename.decode('utf-8')])

                        # Construct metadata
                        meta = {}
                        meta['size'] = size.decode('utf-8')
                        if width_key in metadata[size_key][size] and height_key in metadata[size_key][size]:
                            meta['width'] = metadata[size_key][size][width_key]
                            meta['height'] = metadata[size_key][size][height_key]

                        path = urlparse(url).path
                        dst_path = os.path.join(*([self.output_folder, 'files'] + list(path.split('/'))))
                        dst_dir = os.path.dirname(dst_path)
                        utils.makedirs(dst_dir)
                        LOGGER.info("Downloading {0} => {1}".format(url, dst_path))
                        self.download_url_content_to_file(url, dst_path)
                        dst_url = '/'.join(dst_path.split(os.sep)[2:])
                        links[url] = '/' + dst_url

                        files.append(path)
                        files_meta.append(meta)

        # Prepare result
        result = {}
        result['files'] = files
        result['files_meta'] = files_meta

        # Prepare extraction of more information
        dc_namespace = item.nsmap['dc']
        content_namespace = item.nsmap['content']
        excerpt_namespace = item.nsmap['excerpt']

        def add(result_key, key, namespace=None, filter=None, store_empty=False):
            if namespace is not None:
                value = get_text_tag(item, '{{{0}}}{1}'.format(namespace, key), None)
            else:
                value = get_text_tag(item, key, None)
            if value is not None:
                if filter:
                    value = filter(value)
                if value or store_empty:
                    result[result_key] = value

        add('title', 'title')
        add('date_utc', 'post_date_gmt', namespace=wordpress_namespace)
        add('wordpress_user_name', 'creator', namespace=dc_namespace)
        add('content', 'encoded', namespace=content_namespace)
        add('excerpt', 'encoded', namespace=excerpt_namespace)
        add('description', 'description')

        return result