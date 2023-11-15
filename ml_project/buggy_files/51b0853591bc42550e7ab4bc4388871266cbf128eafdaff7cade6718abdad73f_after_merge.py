    def _import_child(  # pylint: disable=too-many-locals
        cls, stack_properties: dict, parent_stack: "Stack"
    ) -> Optional["Stack"]:
        url = ""
        for event in parent_stack.events():
            if event.physical_id == stack_properties["StackId"] and event.properties:
                url = event.properties["TemplateURL"]
        if url.startswith(parent_stack.template.url_prefix()):
            # Template is part of the project, discovering path
            relative_path = url.replace(parent_stack.template.url_prefix(), "").lstrip(
                "/"
            )
            absolute_path = parent_stack.template.project_root / relative_path
        else:
            try:
                # Assuming template is remote to project and downloading it
                cfn_client = parent_stack.client
                tempate_body = cfn_client.get_template(
                    StackName=stack_properties["StackId"]
                )["TemplateBody"]
                path = parent_stack.template.project_root / Stack.REMOTE_TEMPLATE_PATH
                os.makedirs(path, exist_ok=True)
                fname = (
                    "".join(
                        random.choice(string.ascii_lowercase)  # nosec
                        for _ in range(16)
                    )
                    + ".template"
                )
                absolute_path = path / fname
                template_str = ordered_dump(tempate_body, Dumper=yaml.SafeDumper)
                if not absolute_path.exists():
                    with open(absolute_path, "w") as fh:
                        fh.write(template_str)
            except Exception as e:  # pylint: disable=broad-except
                LOG.warning(
                    f"Failed to attach child stack "
                    f'{stack_properties["StackId"]} {str(e)}'
                )
                LOG.debug("traceback", exc_info=True)
                return None
        template = Template(
            template_path=str(absolute_path),
            project_root=parent_stack.template.project_root,
            url=url,
        )
        stack = cls(
            parent_stack.region,
            stack_properties["StackId"],
            template,
            parent_stack.name,
            parent_stack.uuid,
        )
        stack.set_stack_properties(stack_properties)
        return stack