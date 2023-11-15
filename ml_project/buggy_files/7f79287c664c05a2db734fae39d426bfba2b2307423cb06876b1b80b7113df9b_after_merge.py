    def build(self, hp, inputs=None):
        input_node = nest.flatten(inputs)[0]

        pretrained = self.pretrained
        if input_node.shape[3] not in [1, 3]:
            if self.pretrained:
                raise ValueError(
                    "When pretrained is set to True, expect input to "
                    "have 1 or 3 channels, bug got "
                    "{channels}.".format(channels=input_node.shape[3])
                )
            pretrained = False
        if pretrained is None:
            pretrained = hp.Boolean(PRETRAINED, default=False)
            if pretrained:
                with hp.conditional_scope(PRETRAINED, [True]):
                    trainable = hp.Boolean("trainable", default=False)
        elif pretrained:
            trainable = hp.Boolean("trainable", default=False)

        if len(self.models) > 1:
            version = hp.Choice("version", list(self.models.keys()))
        else:
            version = list(self.models.keys())[0]

        min_size = self.min_size
        if hp.Boolean("imagenet_size", default=False):
            min_size = 224
        if input_node.shape[1] < min_size or input_node.shape[2] < min_size:
            input_node = layers.experimental.preprocessing.Resizing(
                max(min_size, input_node.shape[1]),
                max(min_size, input_node.shape[2]),
            )(input_node)
        if input_node.shape[3] == 1:
            input_node = layers.Concatenate()([input_node] * 3)
        if input_node.shape[3] != 3:
            input_node = layers.Conv2D(filters=3, kernel_size=1, padding="same")(
                input_node
            )

        if pretrained:
            model = self.models[version](weights="imagenet", include_top=False)
            model.trainable = trainable
        else:
            model = self.models[version](
                weights=None, include_top=False, input_shape=input_node.shape[1:]
            )

        return model(input_node)