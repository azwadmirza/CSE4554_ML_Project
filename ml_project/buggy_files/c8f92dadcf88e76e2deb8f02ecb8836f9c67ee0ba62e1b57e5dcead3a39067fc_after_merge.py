def update_non_unique_slugs_for_models(apps, schema_editor):
    models_to_update = ["Category", "Collection"]

    for model in models_to_update:
        Model = apps.get_model("product", model)

        duplicated_slugs = (
            Model.objects.all()
            .values("slug")
            .annotate(duplicated_slug_num=models.Count("slug"))
            .filter(duplicated_slug_num__gt=1)
        )

        slugs_counter = defaultdict(int)
        for data in duplicated_slugs:
            slugs_counter[data["slug"]] = data["duplicated_slug_num"]

        queryset = Model.objects.filter(slug__in=slugs_counter.keys()).order_by("name")

        for instance in queryset:
            slugs_counter[instance.slug] -= 1
            slug = update_slug_to_unique_value(instance.slug, slugs_counter)
            instance.slug = slug
            instance.save(update_fields=["slug"])
            slugs_counter[slug] += 1