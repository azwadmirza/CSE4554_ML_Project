    def collect_templates(
        yml_templates: Dict[Text, List[Any]]
    ) -> Dict[Text, List[Dict[Text, Any]]]:
        """Go through the templates and make sure they are all in dict format
        """
        templates = {}
        for template_key, template_variations in yml_templates.items():
            validated_variations = []
            if template_variations is None:
                raise InvalidDomain(
                    "Utterance '{}' does not have any defined templates.".format(
                        template_key
                    )
                )

            for t in template_variations:
                # templates can either directly be strings or a dict with
                # options we will always create a dict out of them
                if isinstance(t, str):
                    validated_variations.append({"text": t})
                elif "text" not in t and "custom" not in t:
                    raise InvalidDomain(
                        "Utter template '{}' needs to contain either "
                        "'- text: '  or '- custom: ' attribute to be a proper "
                        "template.".format(template_key)
                    )
                else:
                    validated_variations.append(t)

            templates[template_key] = validated_variations
        return templates