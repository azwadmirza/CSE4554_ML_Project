    def transform_template(self):
        """
        Transform the Template using the Serverless Application Model.
        """
        matches = []

        try:
            sam_translator = Translator(managed_policy_map=self._managed_policy_map,
                                        sam_parser=self._sam_parser)

            self._replace_local_codeuri()

            # Tell SAM to use the region we're linting in, this has to be controlled using the default AWS mechanisms, see also:
            # https://github.com/awslabs/serverless-application-model/blob/master/samtranslator/translator/arn_generator.py
            os.environ['AWS_DEFAULT_REGION'] = self._region

            # In the Paser class, within the SAM Translator, they log a warning for when the template
            # does not match the schema. The logger they use is the root logger instead of one scoped to
            # their module. Currently this does not cause templates to fail, so we will suppress this
            # by patching the logging.warning method that is used in that class.
            class WarningSuppressLogger(object):
                """ Patch the Logger in SAM """

                def __init__(self, obj_to_patch):
                    self.obj_to_patch = obj_to_patch

                def __enter__(self):
                    self.obj_to_patch.warning = self.warning

                def __exit__(self, exc_type, exc_val, exc_tb):
                    self.obj_to_patch.warning = self.obj_to_patch.warning

                def warning(self, message):
                    """ Ignore warnings from SAM """
                    pass

            with WarningSuppressLogger(parser.logging):
                self._template = cfnlint.helpers.convert_dict(
                    sam_translator.translate(sam_template=self._template, parameter_values={}))
        except InvalidDocumentException as e:
            for cause in e.causes:
                matches.append(cfnlint.Match(
                    1, 1,
                    1, 1,
                    self._filename, cfnlint.TransformError(), cause.message))

        return matches