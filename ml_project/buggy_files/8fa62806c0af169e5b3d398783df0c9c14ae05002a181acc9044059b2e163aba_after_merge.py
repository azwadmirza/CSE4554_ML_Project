    def __call__(self, result):
        from msrest.pipeline import ClientRawResponse

        if isinstance(result, poller_classes()):
            # most deployment operations return a poller
            result = super(DeploymentOutputLongRunningOperation, self).__call__(result)
            outputs = None
            try:
                outputs = result.properties.outputs
            except AttributeError:  # super.__call__ might return a ClientRawResponse
                pass
            return {key: val['value'] for key, val in outputs.items()} if outputs else {}
        if isinstance(result, ClientRawResponse):
            # --no-wait returns a ClientRawResponse
            return {}

        # --validate returns a 'normal' response
        return result