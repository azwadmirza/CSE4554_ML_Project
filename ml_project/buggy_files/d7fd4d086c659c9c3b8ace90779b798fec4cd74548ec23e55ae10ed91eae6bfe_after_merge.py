def register_tags(filters, actions):
    filters.register('marked-for-op', TagActionFilter)
    filters.register('tag-count', TagCountFilter)

    actions.register('mark-for-op', TagDelayedAction)
    actions.register('tag-trim', TagTrim)

    actions.register('mark', Tag)
    actions.register('tag', Tag)

    actions.register('unmark', RemoveTag)
    actions.register('untag', RemoveTag)
    actions.register('remove-tag', RemoveTag)