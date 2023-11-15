    def read_metadata(self, post, file_metadata_regexp=None, unslugify_titles=False, lang=None):
        """Read the metadata from a post's meta tags, and return a metadata dict."""
        if lang is None:
            lang = LocaleBorg().current_lang
        source_path = post.translated_source_path(lang)

        with io.open(source_path, 'r', encoding='utf-8') as inf:
            data = inf.read()

        metadata = {}
        doc = lxml.html.document_fromstring(data)
        title_tag = doc.find('*//title')
        if title_tag is not None:
            metadata['title'] = title_tag.text
        meta_tags = doc.findall('*//meta')
        for tag in meta_tags:
            k = tag.get('name', '').lower()
            if not k:
                continue
            elif k == 'keywords':
                k = 'tags'
            metadata[k] = tag.get('content', '')
        map_metadata(metadata, 'html_metadata', self.site.config)
        return metadata