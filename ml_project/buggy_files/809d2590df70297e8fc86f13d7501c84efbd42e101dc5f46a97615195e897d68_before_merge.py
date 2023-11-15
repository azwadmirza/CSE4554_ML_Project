    def generate_modifiers(full_data_set, pregen_converter_group):
        """
        Generate standard modifiers.

        :param full_data_set: GenieObjectContainer instance that
                              contains all relevant data for the conversion
                              process.
        :type full_data_set: ...dataformat.aoc.genie_object_container.GenieObjectContainer
        :param pregen_converter_group: GenieObjectGroup instance that stores
                                       pregenerated API objects for referencing with
                                       ForwardRef
        :type pregen_converter_group: ...dataformat.aoc.genie_object_container.GenieObjectGroup
        """
        pregen_nyan_objects = full_data_set.pregen_nyan_objects
        api_objects = full_data_set.nyan_api_objects

        modifier_parent = "engine.modifier.multiplier.MultiplierModifier"
        type_parent = "engine.modifier.multiplier.effect.flat_attribute_change.type.Flyover"
        types_location = "data/aux/modifier/flyover_cliff"

        # =======================================================================
        # Flyover effect multiplier
        # =======================================================================
        modifier_ref_in_modpack = "aux.modifier.flyover_cliff.AttackMultiplierFlyover"
        modifier_raw_api_object = RawAPIObject(modifier_ref_in_modpack,
                                               "AttackMultiplierFlyover", api_objects,
                                               types_location)
        modifier_raw_api_object.set_filename("flyover_cliff")
        modifier_raw_api_object.add_raw_parent(type_parent)

        pregen_converter_group.add_raw_api_object(modifier_raw_api_object)
        pregen_nyan_objects.update({modifier_ref_in_modpack: modifier_raw_api_object})

        # Increases effect value by 25%
        modifier_raw_api_object.add_raw_member("multiplier",
                                               1.25,
                                               modifier_parent)

        # Relative angle to cliff must not be larger than 90°
        modifier_raw_api_object.add_raw_member("relative_angle",
                                               90,
                                               type_parent)

        # Affects all cliffs
        types = [ForwardRef(pregen_converter_group, "aux.game_entity_type.types.Cliff")]
        modifier_raw_api_object.add_raw_member("flyover_types",
                                               types,
                                               type_parent)
        modifier_raw_api_object.add_raw_member("blacklisted_entities",
                                               [],
                                               type_parent)

        # =======================================================================
        # Elevation difference effect multiplier (higher unit)
        # =======================================================================
        modifier_parent = "engine.modifier.multiplier.MultiplierModifier"
        type_parent = "engine.modifier.multiplier.effect.flat_attribute_change.type.ElevationDifferenceHigh"
        types_location = "data/aux/modifier/elevation_difference"

        modifier_ref_in_modpack = "aux.modifier.elevation_difference.AttackMultiplierHigh"
        modifier_raw_api_object = RawAPIObject(modifier_ref_in_modpack,
                                               "AttackMultiplierHigh", api_objects,
                                               types_location)
        modifier_raw_api_object.set_filename("elevation_difference")
        modifier_raw_api_object.add_raw_parent(type_parent)

        pregen_converter_group.add_raw_api_object(modifier_raw_api_object)
        pregen_nyan_objects.update({modifier_ref_in_modpack: modifier_raw_api_object})

        # Increases effect value to 125%
        modifier_raw_api_object.add_raw_member("multiplier",
                                               1.25,
                                               modifier_parent)

        # Min elevation difference is not set

        # =======================================================================
        # Elevation difference effect multiplier (lower unit)
        # =======================================================================
        modifier_parent = "engine.modifier.multiplier.MultiplierModifier"
        type_parent = "engine.modifier.multiplier.effect.flat_attribute_change.type.ElevationDifferenceLow"
        types_location = "data/aux/modifier/elevation_difference"

        modifier_ref_in_modpack = "aux.modifier.elevation_difference.AttackMultiplierLow"
        modifier_raw_api_object = RawAPIObject(modifier_ref_in_modpack,
                                               "AttackMultiplierLow", api_objects,
                                               types_location)
        modifier_raw_api_object.set_filename("elevation_difference")
        modifier_raw_api_object.add_raw_parent(type_parent)

        pregen_converter_group.add_raw_api_object(modifier_raw_api_object)
        pregen_nyan_objects.update({modifier_ref_in_modpack: modifier_raw_api_object})

        # Decreases effect value to 75%
        modifier_raw_api_object.add_raw_member("multiplier",
                                               0.75,
                                               modifier_parent)