def register_tags(filters, actions, id_key):
    filters.register('marked-for-op', TagActionFilter)
    filters.register('tag-count', TagCountFilter)
    actions.register('mark-for-op', TagDelayedAction.set_id(id_key))
    actions.register('tag-trim', TagTrim.set_id(id_key))

    tag = Tag.set_id(id_key)
    actions.register('mark', tag)
    actions.register('tag', tag)

    remove_tag = RemoveTag.set_id(id_key)
    actions.register('unmark', remove_tag)
    actions.register('untag', remove_tag)
    actions.register('remove-tag', remove_tag)