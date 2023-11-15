def generate_unique_slug(instance, slug_values):
    slug = slugify(instance.name) if instance.name else DEFAULT_SLUG_VALUE
    unique_slug = slug
    extension = 1

    while unique_slug in slug_values:
        extension += 1
        unique_slug = f"{slug}-{extension}"

    return unique_slug