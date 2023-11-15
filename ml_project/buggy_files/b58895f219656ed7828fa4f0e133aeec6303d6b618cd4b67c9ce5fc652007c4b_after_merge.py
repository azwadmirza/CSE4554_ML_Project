    def _is_tree_and_contains(obj, path):
        if obj.mode != GIT_MODE_DIR:
            return False
        # see https://github.com/gitpython-developers/GitPython/issues/851
        # `return (i in tree)` doesn't work so here is a workaround:
        for item in obj:
            if _item_basename(item) == path:
                return True
        return False