def create_unique_slug_for_products(apps, schema_editor):
    Product = apps.get_model("product", "Product")

    products = (
        Product.objects.filter(slug__isnull=True).order_by(Lower("name")).iterator()
    )
    previous_char = ""
    slug_values = []
    for product in products:
        first_char = product.name[0].lower()
        if first_char != previous_char:
            previous_char = first_char
            slug_values = Product.objects.filter(
                slug__istartswith=first_char
            ).values_list("slug", flat=True)

        slug = generate_unique_slug(product, slug_values)
        product.slug = slug
        slug_values.append(slug)