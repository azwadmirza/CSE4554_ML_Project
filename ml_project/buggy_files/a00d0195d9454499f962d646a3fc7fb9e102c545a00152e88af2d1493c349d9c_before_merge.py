    def _metric_tags(self, metric_name, val, sample, scraper_config, hostname=None):
        custom_tags = scraper_config['custom_tags']
        _tags = list(custom_tags)
        _tags.extend(scraper_config['_metric_tags'])
        for label_name, label_value in iteritems(sample[self.SAMPLE_LABELS]):
            if label_name not in scraper_config['exclude_labels']:
                tag_name = scraper_config['labels_mapper'].get(label_name, label_name)
                _tags.append('{}:{}'.format(tag_name, label_value))
        return self._finalize_tags_to_submit(
            _tags, metric_name, val, sample, custom_tags=custom_tags, hostname=hostname
        )