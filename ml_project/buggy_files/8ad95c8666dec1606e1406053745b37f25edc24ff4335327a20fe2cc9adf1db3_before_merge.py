    def resolve_category(root: models.Product, info):
        return CategoryByIdLoader(info.context).load(root.category_id)