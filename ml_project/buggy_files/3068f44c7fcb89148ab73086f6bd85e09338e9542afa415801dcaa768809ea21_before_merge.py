    def start_battle(self, game, action):
        """Start a battle and switch to the combat module. The parameters must contain an NPC id
        in the NPC database.

        :param game: The main game object that contains all the game's variables.
        :param action: The action (tuple) retrieved from the database that contains the action's
            parameters

        :type game: core.control.Control
        :type action: Tuple

        :rtype: None
        :returns: None

        Valid Parameters: npc_id

        **Examples:**

        >>> action.__dict__
        {
            "type": "start_battle",
            "parameters": [
                "1"
            ]
        }

        """
        # Don't start a battle if we don't even have monsters in our party yet.
        if not self.check_battle_legal(game.player1):
            return False

        # Stop movement and keypress on the server.
        if game.isclient or game.ishost:
                game.client.update_player(game.player1.facing, event_type="CLIENT_START_BATTLE")

        # Start combat
        npc_id = int(action.parameters[0])

        # Create an NPC object that will be used as our opponent
        npc = player.Npc()

        # Look up the NPC's details from our NPC database
        npcs = db.JSONDatabase()
        npcs.load("npc")
        npc_details = npcs.database['npc'][npc_id]

        # Set the NPC object with the details fetched from the database.
        npc.name = npc_details['name']

        # Set the NPC object's AI model.
        npc.ai = ai.AI()

        # Look up the NPC's monster party
        npc_party = npc_details['monsters']

        # Look up the monster's details
        monsters = db.JSONDatabase()
        monsters.load("monster")

        # Look up each monster in the NPC's party
        for npc_monster_details in npc_party:
            results = monsters.database['monster'][npc_monster_details['monster_id']]

            # Create a monster object for each monster the NPC has in their party.
            current_monster = monster.Monster()
            current_monster.load_from_db(npc_monster_details['monster_id'])
            current_monster.name = npc_monster_details['name']
            current_monster.monster_id = npc_monster_details['monster_id']
            current_monster.level = npc_monster_details['level']
            current_monster.hp = npc_monster_details['hp']
            current_monster.current_hp = npc_monster_details['hp']
            current_monster.attack = npc_monster_details['attack']
            current_monster.defense = npc_monster_details['defense']
            current_monster.speed = npc_monster_details['speed']
            current_monster.special_attack = npc_monster_details['special_attack']
            current_monster.special_defense = npc_monster_details['special_defense']
            current_monster.experience_give_modifier = npc_monster_details['exp_give_mod']
            current_monster.experience_required_modifier = npc_monster_details['exp_req_mod']

            current_monster.type1 = results['types'][0]

            current_monster.set_level(current_monster.level)

            if len(results['types']) > 1:
                current_monster.type2 = results['types'][1]

            current_monster.load_sprite_from_db()

            pound = technique.Technique('Pound')

            current_monster.learn(pound)

            # Add our monster to the NPC's party
            npc.monsters.append(current_monster)

        # Add our players and setup combat
        game.push_state("CombatState", players=(game.player1, npc), combat_type="trainer")

        # Flash the screen before combat
        # game.push_state("FlashTransition")

        # Start some music!
        logger.info("Playing battle music!")
        filename = "147066_pokemon.ogg"

        mixer.music.load(prepare.BASEDIR + "resources/music/" + filename)
        mixer.music.play(-1)