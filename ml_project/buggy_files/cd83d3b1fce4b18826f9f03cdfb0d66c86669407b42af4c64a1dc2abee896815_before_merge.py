def create_unique_slug_for_warehouses(apps, schema_editor):
    Warehouse = apps.get_model("warehouse", "Warehouse")

    warehouses = (
        Warehouse.objects.filter(slug__isnull=True).order_by(Lower("name")).iterator()
    )
    previous_char = ""
    slug_values = []
    for warehouse in warehouses:
        first_char = warehouse.name[0].lower()
        if first_char != previous_char:
            previous_char = first_char
            slug_values = Warehouse.objects.filter(
                slug__istartswith=first_char
            ).values_list("slug", flat=True)

        slug = generate_unique_slug(warehouse, slug_values)
        warehouse.slug = slug
        slug_values.append(slug)