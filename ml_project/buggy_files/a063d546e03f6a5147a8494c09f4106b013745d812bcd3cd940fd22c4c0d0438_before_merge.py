def update_products_minimal_variant_prices_of_catalogues(
    product_ids=None, category_ids=None, collection_ids=None
):
    # Building the matching products query
    q_list = []
    if product_ids:
        q_list.append(Q(pk__in=product_ids))
    if category_ids:
        q_list.append(Q(category_id__in=category_ids))
    if collection_ids:
        q_list.append(Q(collectionproduct__collection_id__in=collection_ids))
    # Asserting that the function was called with some ids
    if not q_list:
        raise ValueError(
            "Provide at least one of the ID lists:\n"
            "\tproduct_ids,\n"
            "\tcategory_ids,\n"
            "\tcollection_ids."
        )
    # Querying the products
    q_or = reduce(operator.or_, q_list)
    products = Product.objects.filter(q_or).distinct()

    update_products_minimal_variant_prices(products)