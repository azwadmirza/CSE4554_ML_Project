    def create_subnet(
        self,
        vpc_id,
        cidr_block,
        availability_zone=None,
        availability_zone_id=None,
        context=None,
        tags=[],
    ):
        subnet_id = random_subnet_id()
        vpc = self.get_vpc(
            vpc_id
        )  # Validate VPC exists and the supplied CIDR block is a subnet of the VPC's
        vpc_cidr_blocks = [
            ipaddress.IPv4Network(
                six.text_type(cidr_block_association["cidr_block"]), strict=False
            )
            for cidr_block_association in vpc.get_cidr_block_association_set()
        ]
        try:
            subnet_cidr_block = ipaddress.IPv4Network(
                six.text_type(cidr_block), strict=False
            )
        except ValueError:
            raise InvalidCIDRBlockParameterError(cidr_block)

        subnet_in_vpc_cidr_range = False
        for vpc_cidr_block in vpc_cidr_blocks:
            if (
                vpc_cidr_block.network_address <= subnet_cidr_block.network_address
                and vpc_cidr_block.broadcast_address
                >= subnet_cidr_block.broadcast_address
            ):
                subnet_in_vpc_cidr_range = True
                break

        if not subnet_in_vpc_cidr_range:
            raise InvalidSubnetRangeError(cidr_block)

        for subnet in self.get_all_subnets(filters={"vpc-id": vpc_id}):
            if subnet.cidr.overlaps(subnet_cidr_block):
                raise InvalidSubnetConflictError(cidr_block)

        # if this is the first subnet for an availability zone,
        # consider it the default
        default_for_az = str(availability_zone not in self.subnets).lower()
        map_public_ip_on_launch = default_for_az

        if availability_zone is None and not availability_zone_id:
            availability_zone = "us-east-1a"
        try:
            if availability_zone:
                availability_zone_data = next(
                    zone
                    for zones in RegionsAndZonesBackend.zones.values()
                    for zone in zones
                    if zone.name == availability_zone
                )
            elif availability_zone_id:
                availability_zone_data = next(
                    zone
                    for zones in RegionsAndZonesBackend.zones.values()
                    for zone in zones
                    if zone.zone_id == availability_zone_id
                )

        except StopIteration:
            raise InvalidAvailabilityZoneError(
                availability_zone,
                ", ".join(
                    [
                        zone.name
                        for zones in RegionsAndZonesBackend.zones.values()
                        for zone in zones
                    ]
                ),
            )
        subnet = Subnet(
            self,
            subnet_id,
            vpc_id,
            cidr_block,
            availability_zone_data,
            default_for_az,
            map_public_ip_on_launch,
            owner_id=context.get_current_user() if context else OWNER_ID,
            assign_ipv6_address_on_creation=False,
        )

        for tag in tags:
            tag_key = tag.get("Key")
            tag_value = tag.get("Value")
            subnet.add_tag(tag_key, tag_value)

        # AWS associates a new subnet with the default Network ACL
        self.associate_default_network_acl_with_subnet(subnet_id, vpc_id)
        self.subnets[availability_zone][subnet_id] = subnet
        return subnet