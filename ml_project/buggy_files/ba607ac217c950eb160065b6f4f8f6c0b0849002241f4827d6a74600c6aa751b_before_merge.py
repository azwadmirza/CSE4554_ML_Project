def _init():
    """
    This function is called automatically by the launcher only after
    Evennia has fully initialized all its models. It sets up the API
    in a safe environment where all models are available already.
    """
    global DefaultAccount, DefaultObject, DefaultGuest, DefaultCharacter
    global DefaultRoom, DefaultExit, DefaultChannel, DefaultScript
    global ObjectDB, AccountDB, ScriptDB, ChannelDB, Msg
    global Command, CmdSet, default_cmds, syscmdkeys, InterruptCommand
    global search_object, search_script, search_account, search_channel
    global search_help, search_tag, search_message
    global create_object, create_script, create_account, create_channel
    global create_message, create_help_entry
    global signals
    global settings, lockfuncs, logger, utils, gametime, ansi, spawn, managers
    global contrib, TICKER_HANDLER, MONITOR_HANDLER, SESSION_HANDLER
    global CHANNEL_HANDLER, TASK_HANDLER
    global GLOBAL_SCRIPTS, OPTION_CLASSES
    global EvMenu, EvTable, EvForm, EvMore, EvEditor
    global ANSIString

    global BASE_ACCOUNT_TYPECLASS, BASE_OBJECT_TYPECLASS, BASE_CHARACTER_TYPECLASS
    global BASE_ROOM_TYPECLASS, BASE_EXIT_TYPECLASS, BASE_CHANNEL_TYPECLASS
    global BASE_SCRIPT_TYPECLASS, BASE_GUEST_TYPECLASS

    # Parent typeclasses
    from .accounts.accounts import DefaultAccount
    from .accounts.accounts import DefaultGuest
    from .objects.objects import DefaultObject
    from .objects.objects import DefaultCharacter
    from .objects.objects import DefaultRoom
    from .objects.objects import DefaultExit
    from .comms.comms import DefaultChannel
    from .scripts.scripts import DefaultScript

    # Database models
    from .objects.models import ObjectDB
    from .accounts.models import AccountDB
    from .scripts.models import ScriptDB
    from .comms.models import ChannelDB
    from .comms.models import Msg

    # commands
    from .commands.command import Command, InterruptCommand
    from .commands.cmdset import CmdSet

    # search functions
    from .utils.search import search_object
    from .utils.search import search_script
    from .utils.search import search_account
    from .utils.search import search_message
    from .utils.search import search_channel
    from .utils.search import search_help
    from .utils.search import search_tag

    # create functions
    from .utils.create import create_object
    from .utils.create import create_script
    from .utils.create import create_account
    from .utils.create import create_channel
    from .utils.create import create_message
    from .utils.create import create_help_entry

    # utilities
    from django.conf import settings
    from .locks import lockfuncs
    from .utils import logger
    from .utils import gametime
    from .utils import ansi
    from .prototypes.spawner import spawn
    from . import contrib
    from .utils.evmenu import EvMenu
    from .utils.evtable import EvTable
    from .utils.evmore import EvMore
    from .utils.evform import EvForm
    from .utils.eveditor import EvEditor
    from .utils.ansi import ANSIString
    from .server import signals

    # handlers
    from .scripts.tickerhandler import TICKER_HANDLER
    from .scripts.taskhandler import TASK_HANDLER
    from .server.sessionhandler import SESSION_HANDLER
    from .comms.channelhandler import CHANNEL_HANDLER
    from .scripts.monitorhandler import MONITOR_HANDLER

    # containers
    from .utils.containers import GLOBAL_SCRIPTS
    from .utils.containers import OPTION_CLASSES

    # API containers

    class _EvContainer(object):
        """
        Parent for other containers

        """

        def _help(self):
            "Returns list of contents"
            names = [name for name in self.__class__.__dict__ if not name.startswith("_")]
            names += [name for name in self.__dict__ if not name.startswith("_")]
            print(self.__doc__ + "-" * 60 + "\n" + ", ".join(names))

        help = property(_help)

    class DBmanagers(_EvContainer):
        """
        Links to instantiated Django database managers. These are used
        to perform more advanced custom database queries than the standard
        search functions allow.

        helpentries - HelpEntry.objects
        accounts - AccountDB.objects
        scripts - ScriptDB.objects
        msgs    - Msg.objects
        channels - Channel.objects
        objects - ObjectDB.objects
        serverconfigs - ServerConfig.objects
        tags - Tags.objects
        attributes - Attributes.objects

        """

        from .help.models import HelpEntry
        from .accounts.models import AccountDB
        from .scripts.models import ScriptDB
        from .comms.models import Msg, ChannelDB
        from .objects.models import ObjectDB
        from .server.models import ServerConfig
        from .typeclasses.attributes import Attribute
        from .typeclasses.tags import Tag

        # create container's properties
        helpentries = HelpEntry.objects
        accounts = AccountDB.objects
        scripts = ScriptDB.objects
        msgs = Msg.objects
        channels = ChannelDB.objects
        objects = ObjectDB.objects
        serverconfigs = ServerConfig.objects
        attributes = Attribute.objects
        tags = Tag.objects
        # remove these so they are not visible as properties
        del HelpEntry, AccountDB, ScriptDB, Msg, ChannelDB
        # del ExternalChannelConnection
        del ObjectDB, ServerConfig, Tag, Attribute

    managers = DBmanagers()
    del DBmanagers

    class DefaultCmds(_EvContainer):
        """
        This container holds direct shortcuts to all default commands in Evennia.

        To access in code, do 'from evennia import default_cmds' then
        access the properties on the imported default_cmds object.

        """

        from .commands.default.cmdset_character import CharacterCmdSet
        from .commands.default.cmdset_account import AccountCmdSet
        from .commands.default.cmdset_unloggedin import UnloggedinCmdSet
        from .commands.default.cmdset_session import SessionCmdSet
        from .commands.default.muxcommand import MuxCommand, MuxAccountCommand

        def __init__(self):
            "populate the object with commands"

            def add_cmds(module):
                "helper method for populating this object with cmds"
                from evennia.utils import utils

                cmdlist = utils.variable_from_module(module, module.__all__)
                self.__dict__.update(dict([(c.__name__, c) for c in cmdlist]))

            from .commands.default import (
                admin,
                batchprocess,
                building,
                comms,
                general,
                account,
                help,
                system,
                unloggedin,
            )

            add_cmds(admin)
            add_cmds(building)
            add_cmds(batchprocess)
            add_cmds(building)
            add_cmds(comms)
            add_cmds(general)
            add_cmds(account)
            add_cmds(help)
            add_cmds(system)
            add_cmds(unloggedin)

    default_cmds = DefaultCmds()
    del DefaultCmds

    class SystemCmds(_EvContainer):
        """
        Creating commands with keys set to these constants will make
        them system commands called as a replacement by the parser when
        special situations occur. If not defined, the hard-coded
        responses in the server are used.

        CMD_NOINPUT - no input was given on command line
        CMD_NOMATCH - no valid command key was found
        CMD_MULTIMATCH - multiple command matches were found
        CMD_CHANNEL - the command name is a channel name
        CMD_LOGINSTART - this command will be called as the very
                         first command when an account connects to
                         the server.

        To access in code, do 'from evennia import syscmdkeys' then
        access the properties on the imported syscmdkeys object.

        """

        from .commands import cmdhandler

        CMD_NOINPUT = cmdhandler.CMD_NOINPUT
        CMD_NOMATCH = cmdhandler.CMD_NOMATCH
        CMD_MULTIMATCH = cmdhandler.CMD_MULTIMATCH
        CMD_CHANNEL = cmdhandler.CMD_CHANNEL
        CMD_LOGINSTART = cmdhandler.CMD_LOGINSTART
        del cmdhandler

    syscmdkeys = SystemCmds()
    del SystemCmds
    del _EvContainer

    # delayed starts - important so as to not back-access evennia before it has
    # finished initializing
    GLOBAL_SCRIPTS.start()
    from .prototypes import prototypes
    prototypes.load_module_prototypes()
    del prototypes