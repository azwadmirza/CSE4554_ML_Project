    def resolve_category(root: models.Product, info):
        category_id = root.category_id
        if category_id is None:
            return None

        return CategoryByIdLoader(info.context).load(category_id)