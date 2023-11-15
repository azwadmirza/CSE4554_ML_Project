    def process_attached(self, client, associated_addrs):
        for aa in list(associated_addrs):
            try:
                client.disassociate_address(AssociationId=aa['AssociationId'])
            except BotoClientError as e:
                # If its already been diassociated ignore, else raise.
                if not(e.response['Error']['Code'] == 'InvalidAssocationID.NotFound' and
                       aa['AssocationId'] in e.response['Error']['Message']):
                    raise e
                associated_addrs.remove(aa)
        return associated_addrs