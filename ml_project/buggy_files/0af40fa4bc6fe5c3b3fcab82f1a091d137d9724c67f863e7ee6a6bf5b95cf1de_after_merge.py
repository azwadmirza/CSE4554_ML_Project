def _maybe_set_tags(tags, obj):
    if tags:
        # Not all objects in Boto have an 'add_tags()' method.
        try:
            obj.add_tags(tags)

        except AttributeError:
            for tag, value in tags.items():
                obj.add_tag(tag, value)

        log.debug('The following tags: {0} were added to {1}'.format(', '.join(tags), obj))