    def _pick_working_subscription(subscriptions):
        from azure.mgmt.resource.subscriptions.models import SubscriptionState
        s = next((x for x in subscriptions if x['state'] == SubscriptionState.enabled.value), None)
        return s or subscriptions[0]