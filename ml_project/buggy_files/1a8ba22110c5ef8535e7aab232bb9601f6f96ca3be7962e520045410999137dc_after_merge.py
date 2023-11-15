def validate_image_file(file, field_name):
    """Validate if the file is an image."""
    if not file:
        raise ValidationError(
            {field_name: ValidationError("File is required", code="required")}
        )
    if not file.content_type.startswith("image/"):
        raise ValidationError(
            {field_name: ValidationError("Invalid file type", code="invalid")}
        )