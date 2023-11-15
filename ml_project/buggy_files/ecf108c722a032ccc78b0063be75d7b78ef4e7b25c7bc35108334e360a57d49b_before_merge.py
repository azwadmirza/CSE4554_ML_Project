def create_unique_slugs_for_producttypes(apps, schema_editor):
    ProductType = apps.get_model("product", "ProductType")

    product_types = (
        ProductType.objects.filter(slug__isnull=True).order_by(Lower("name")).iterator()
    )
    previous_char = ""
    slug_values = []
    for product_type in product_types:
        first_char = product_type.name[0].lower()
        if first_char != previous_char:
            previous_char = first_char
            slug_values = ProductType.objects.filter(
                slug__istartswith=first_char
            ).values_list("slug", flat=True)

        slug = generate_unique_slug(product_type, slug_values)
        product_type.slug = slug
        slug_values.append(slug)