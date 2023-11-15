def create_unique_slug_for_warehouses(apps, schema_editor):
    Warehouse = apps.get_model("warehouse", "Warehouse")

    warehouses = (
        Warehouse.objects.filter(slug__isnull=True).order_by(Lower("name")).iterator()
    )
    previous_char = None
    slug_values = []
    for warehouse in warehouses:
        if warehouse.name:
            first_char = warehouse.name[0].lower()
            if first_char != previous_char:
                previous_char = first_char
                slug_values = list(
                    Warehouse.objects.filter(slug__istartswith=first_char).values_list(
                        "slug", flat=True
                    )
                )
        elif previous_char is None:
            previous_char = ""
            slug_values = list(
                Warehouse.objects.filter(
                    slug__istartswith=DEFAULT_SLUG_VALUE
                ).values_list("slug", flat=True)
            )

        slug = generate_unique_slug(warehouse, slug_values)
        warehouse.slug = slug
        warehouse.save(update_fields=["slug"])
        slug_values.append(slug)