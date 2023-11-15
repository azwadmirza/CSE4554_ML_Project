def _get_relations(package, schema, current_resource_name=None):
    # It's based on the following code:
    # https://github.com/frictionlessdata/datapackage-py/blob/master/datapackage/resource.py#L393

    # Prepare relations
    relations = {}
    for fk in schema.foreign_keys:
        resource_name = fk['reference'].get('resource')
        package_name = fk['reference'].get('package')
        resource = None

        # Self-referenced resource
        if not resource_name:
            for item in package.resources:
                if item.name == current_resource_name:
                    resource = item

        # Internal resource
        elif not package_name:
            resource = package.get_resource(resource_name)

        # External resource (experimental)
        # For now, we rely on uniqueness of resource names and support relative paths
        else:
            descriptor = package_name
            if not descriptor.startswith('http'):
                descriptor = '/'.join([package.base_path, package_name])
            package = Package(descriptor)
            resource = package.get_resource(resource_name)

        # Add to relations (can be None)
        relations[resource_name] = resource
        if resource and resource.tabular:
            relations[resource_name] = resource.read(keyed=True)

    return relations