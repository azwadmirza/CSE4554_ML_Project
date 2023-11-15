    def __init__(self):
        self.audit_lookup = {
            0: "No auditing",
            1: "Success",
            2: "Failure",
            3: "Success, Failure",
            "Not Defined": "Not Defined",
            None: "Not Defined",
        }
        self.advanced_audit_lookup = {
            0: "No Auditing",
            1: "Success",
            2: "Failure",
            3: "Success and Failure",
            None: "Not Configured",
        }
        self.sc_removal_lookup = {
            0: "No Action",
            1: "Lock Workstation",
            2: "Force Logoff",
            3: "Disconnect if a Remote Desktop Services session",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.uac_admin_prompt_lookup = {
            0: "Elevate without prompting",
            1: "Prompt for credentials on the secure desktop",
            2: "Prompt for consent on the secure desktop",
            3: "Prompt for credentials",
            4: "Prompt for consent",
            5: "Prompt for consent for non-Windows binaries",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.uac_user_prompt_lookup = {
            0: "Automatically deny elevation requests",
            1: "Prompt for credentials on the secure desktop",
            3: "Prompt for credentials",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.enabled_one_disabled_zero = {
            0: "Disabled",
            1: "Enabled",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.enabled_one_disabled_zero_transform = {
            "Get": "_dict_lookup",
            "Put": "_dict_lookup",
            "GetArgs": {
                "lookup": self.enabled_one_disabled_zero,
                "value_lookup": False,
            },
            "PutArgs": {
                "lookup": self.enabled_one_disabled_zero,
                "value_lookup": True,
            },
        }
        self.s4u2self_options = {
            0: "Default",
            1: "Enabled",
            2: "Disabled",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.audit_transform = {
            "Get": "_dict_lookup",
            "Put": "_dict_lookup",
            "GetArgs": {"lookup": self.audit_lookup, "value_lookup": False},
            "PutArgs": {"lookup": self.audit_lookup, "value_lookup": True},
        }
        self.advanced_audit_transform = {
            "Get": "_dict_lookup",
            "Put": "_dict_lookup",
            "GetArgs": {"lookup": self.advanced_audit_lookup, "value_lookup": False},
            "PutArgs": {"lookup": self.advanced_audit_lookup, "value_lookup": True},
        }
        self.enabled_one_disabled_zero_strings = {
            "0": "Disabled",
            "1": "Enabled",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.enabled_one_disabled_zero_strings_transform = {
            "Get": "_dict_lookup",
            "Put": "_dict_lookup",
            "GetArgs": {
                "lookup": self.enabled_one_disabled_zero_strings,
                "value_lookup": False,
            },
            "PutArgs": {
                "lookup": self.enabled_one_disabled_zero_strings,
                "value_lookup": True,
            },
        }
        self.security_options_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Local Policies",
            "Security Options",
        ]
        self.windows_firewall_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Windows Firewall with Advanced Security",
            "Windows Firewall with Advanced Security - Local Group Policy Object",
        ]
        self.password_policy_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Account Policies",
            "Password Policy",
        ]
        self.audit_policy_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Local Policies",
            "Audit Policy",
        ]
        self.advanced_audit_policy_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Advanced Audit Policy Configuration",
            "System Audit Policies - Local Group Policy Object",
        ]
        self.account_lockout_policy_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Account Policies",
            "Account Lockout Policy",
        ]
        self.user_rights_assignment_gpedit_path = [
            "Computer Configuration",
            "Windows Settings",
            "Security Settings",
            "Local Policies",
            "User Rights Assignment",
        ]
        self.block_ms_accounts = {
            0: "This policy is disabled",
            1: "Users can't add Microsoft accounts",
            3: "Users can't add or log on with Microsoft accounts",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ldap_server_signing_requirements = {
            1: "None",
            2: "Require signing",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.smb_server_name_hardening_levels = {
            0: "Off",
            1: "Accept if provided by client",
            2: "Required from client",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.locked_session_user_info = {
            1: "User display name, domain and user names",
            2: "User display name only",
            3: "Do not display user information",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.force_guest = {
            0: "Classic - local users authenticate as themselves",
            1: "Guest only - local users authenticate as Guest",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.force_key_protection = {
            0: "User input is not required when new keys are stored and used",
            1: "User is prompted when the key is first used",
            2: "User must enter a password each time they use a key",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.firewall_inbound_connections = {
            "blockinbound": "Block (default)",
            "blockinboundalways": "Block all connections",
            "allowinbound": "Allow",
            "notconfigured": "Not configured",
        }
        self.firewall_outbound_connections = {
            "blockoutbound": "Block",
            "allowoutbound": "Allow (default)",
            "notconfigured": "Not configured",
        }
        self.firewall_rule_merging = {
            "enable": "Yes (default)",
            "disable": "No",
            "notconfigured": "Not configured",
        }
        self.firewall_log_packets_connections = {
            "enable": "Yes",
            "disable": "No (default)",
            "notconfigured": "Not configured",
        }
        self.firewall_notification = {
            "enable": "Yes",
            "disable": "No",
            "notconfigured": "Not configured",
        }
        self.firewall_state = {
            "on": "On (recommended)",
            "off": "Off",
            "notconfigured": "Not configured",
        }
        self.krb_encryption_types = {
            0: "No minimum",
            1: "DES_CBC_CRC",
            2: "DES_CBD_MD5",
            4: "RC4_HMAC_MD5",
            8: "AES128_HMAC_SHA1",
            16: "AES256_HMAC_SHA1",
            2147483616: "Future Encryption Types",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.lm_compat_levels = {
            0: "Send LM & NTLM response",
            1: "Send LM & NTLM - use NTLMv2 session security if negotiated",
            2: "Send NTLM response only",
            3: "Send NTLMv2 response only",
            4: "Send NTLMv2 response only. Refuse LM",
            5: "Send NTLMv2 response only. Refuse LM & NTLM",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ldap_signing_reqs = {
            0: "None",
            1: "Negotiate signing",
            2: "Require signing",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ntlm_session_security_levels = {
            0: "No minimum",
            524288: "Require NTLMv2 session security",
            536870912: "Require 128-bit encryption",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ntlm_audit_settings = {
            0: "Disable",
            1: "Enable auditing for domain accounts",
            2: "Enable auditing for all accounts",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ntlm_domain_audit_settings = {
            0: "Disable",
            1: "Enable for domain accounts to domain servers",
            3: "Enable for domain accounts",
            5: "Enable for domain servers",
            7: "Enable all",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.incoming_ntlm_settings = {
            0: "Allow all",
            1: "Deny all domain accounts",
            2: "Deny all accounts",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.ntlm_domain_auth_settings = {
            0: "Disable",
            1: "Deny for domain accounts to domain servers",
            3: "Deny for domain accounts",
            5: "Deny for domain servers",
            7: "Deny all",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.outgoing_ntlm_settings = {
            0: "Allow all",
            1: "Audit all",
            2: "Deny all",
            None: "Not Defined",
            "(value not set)": "Not Defined",
        }
        self.enabled_one_disabled_zero_no_not_defined = {
            0: "Disabled",
            1: "Enabled",
        }
        self.enabled_one_disabled_zero_no_not_defined_transform = {
            "Get": "_dict_lookup",
            "Put": "_dict_lookup",
            "GetArgs": {
                "lookup": self.enabled_one_disabled_zero_no_not_defined,
                "value_lookup": False,
            },
            "PutArgs": {
                "lookup": self.enabled_one_disabled_zero_no_not_defined,
                "value_lookup": True,
            },
        }
        self.policies = {
            "Machine": {
                "lgpo_section": "Computer Configuration",
                "policies": {
                    "StartupScripts": {
                        "Policy": "Startup Scripts",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Startup",
                        ],
                        "ScriptIni": {
                            "Section": "Startup",
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "scripts.ini",
                            ),
                        },
                    },
                    "StartupPowershellScripts": {
                        "Policy": "Startup Powershell Scripts",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Startup",
                        ],
                        "ScriptIni": {
                            "Section": "Startup",
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "psscripts.ini",
                            ),
                        },
                    },
                    "StartupPowershellScriptOrder": {
                        "Policy": "Startup - For this GPO, run scripts in the "
                        "following order",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Startup",
                        ],
                        "ScriptIni": {
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "psscripts.ini",
                            ),
                            "Section": "ScriptsConfig",
                            "SettingName": "StartExecutePSFirst",
                            "Settings": ["true", "false", None],
                        },
                        "Transform": {
                            "Get": "_powershell_script_order_conversion",
                            "Put": "_powershell_script_order_reverse_conversion",
                        },
                    },
                    "ShutdownScripts": {
                        "Policy": "Shutdown Scripts",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Shutdown",
                        ],
                        "ScriptIni": {
                            "Section": "Shutdown",
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "scripts.ini",
                            ),
                        },
                    },
                    "ShutdownPowershellScripts": {
                        "Policy": "Shutdown Powershell Scripts",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Shutdown",
                        ],
                        "ScriptIni": {
                            "Section": "Shutdown",
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "psscripts.ini",
                            ),
                        },
                    },
                    "ShutdownPowershellScriptOrder": {
                        "Policy": "Shutdown - For this GPO, run scripts in the "
                        "following order",
                        "lgpo_section": [
                            "Computer Configuration",
                            "Windows Settings",
                            "Scripts (Startup/Shutdown)",
                            "Shutdown",
                        ],
                        "ScriptIni": {
                            "IniPath": os.path.join(
                                os.getenv("WINDIR"),
                                "System32",
                                "GroupPolicy",
                                "Machine",
                                "Scripts",
                                "psscripts.ini",
                            ),
                            "Section": "ScriptsConfig",
                            "SettingName": "EndExecutePSFirst",
                            "Settings": ["true", "false", None],
                        },
                        "Transform": {
                            "Get": "_powershell_script_order_conversion",
                            "Put": "_powershell_script_order_reverse_conversion",
                        },
                    },
                    "LSAAnonymousNameLookup": {
                        "Policy": "Network access: Allow anonymous SID/Name "
                        "translation",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "Secedit": {
                            "Option": "LSAAnonymousNameLookup",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "RestrictAnonymousSam": {
                        "Policy": "Network access: Do not allow anonymous "
                        "enumeration of SAM accounts",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "RestrictAnonymousSam",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "RestrictRemoteSAM": {
                        "Policy": "Network access: Restrict clients allowed to "
                        "make remote calls to SAM",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa",
                            "Value": "RestrictRemoteSAM",
                            "Type": "REG_SZ",
                        },
                        "Transform": {"Put": "_string_put_transform"},
                    },
                    "RestrictAnonymous": {
                        "Policy": "Network access: Do not allow anonymous "
                        "enumeration of SAM accounts and shares",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "RestrictAnonymous",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "DisableDomainCreds": {
                        "Policy": "Network access: Do not allow storage of "
                        "passwords and credentials for network "
                        "authentication",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "DisableDomainCreds",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EveryoneIncludesAnonymous": {
                        "Policy": "Network access: Let Everyone permissions "
                        "apply to anonymous users",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "everyoneincludesanonymous",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "NullSessionPipes": {
                        "Policy": "Network access: Named Pipes that can be "
                        "accessed anonymously",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "NullSessionPipes",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "RemoteRegistryExactPaths": {
                        "Policy": "Network access: Remotely accessible "
                        "registry paths",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\"
                            "SecurePipeServers\\winreg\\"
                            "AllowedExactPaths",
                            "Value": "Machine",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "RemoteRegistryPaths": {
                        "Policy": "Network access: Remotely accessible "
                        "registry paths and sub-paths",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\"
                            "SecurePipeServers\\winreg\\AllowedPaths",
                            "Value": "Machine",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "RestrictNullSessAccess": {
                        "Policy": "Network access: Restrict anonymous access "
                        "to Named Pipes and Shares",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "RestrictNullSessAccess",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "NullSessionShares": {
                        "Policy": "Network access: Shares that can be accessed "
                        "anonymously",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "NullSessionShares",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "ForceGuest": {
                        "Policy": "Network access: Sharing and security model "
                        "for local accounts",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.force_guest.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "ForceGuest",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.force_guest,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.force_guest,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainState": {
                        "Policy": "Network firewall: Domain: State",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - On (recommended)
                        # - Off
                        # - Not configured
                        "Settings": self.firewall_state.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "state",
                            "Option": "State",  # Unused, but needed
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateState": {
                        "Policy": "Network firewall: Private: State",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - On (recommended)
                        # - Off
                        # - Not configured
                        "Settings": self.firewall_state.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "state",
                            "Option": "State",  # Unused, but needed
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicState": {
                        "Policy": "Network firewall: Public: State",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - On (recommended)
                        # - Off
                        # - Not configured
                        "Settings": self.firewall_state.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "state",
                            "Option": "State",  # Unused, but needed
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_state,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainInboundConnections": {
                        "Policy": "Network firewall: Domain: Inbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block (default)
                        # - Block all connections
                        # - Allow
                        # - Not configured
                        "Settings": self.firewall_inbound_connections.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "firewallpolicy",
                            "Option": "Inbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateInboundConnections": {
                        "Policy": "Network firewall: Private: Inbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block (default)
                        # - Block all connections
                        # - Allow
                        # - Not configured
                        "Settings": self.firewall_inbound_connections.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "firewallpolicy",
                            "Option": "Inbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicInboundConnections": {
                        "Policy": "Network firewall: Public: Inbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block (default)
                        # - Block all connections
                        # - Allow
                        # - Not configured
                        "Settings": self.firewall_inbound_connections.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "firewallpolicy",
                            "Option": "Inbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_inbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainOutboundConnections": {
                        "Policy": "Network firewall: Domain: Outbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block
                        # - Allow (default)
                        # - Not configured
                        "Settings": self.firewall_outbound_connections.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "firewallpolicy",
                            "Option": "Outbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateOutboundConnections": {
                        "Policy": "Network firewall: Private: Outbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block
                        # - Allow (default)
                        # - Not configured
                        "Settings": self.firewall_outbound_connections.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "firewallpolicy",
                            "Option": "Outbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicOutboundConnections": {
                        "Policy": "Network firewall: Public: Outbound connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Block
                        # - Allow (default)
                        # - Not configured
                        "Settings": self.firewall_outbound_connections.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "firewallpolicy",
                            "Option": "Outbound",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_outbound_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainSettingsNotification": {
                        "Policy": "Network firewall: Domain: Settings: Display a notification",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No
                        # - Not configured
                        "Settings": self.firewall_notification.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "settings",
                            "Option": "InboundUserNotification",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateSettingsNotification": {
                        "Policy": "Network firewall: Private: Settings: Display a notification",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No
                        # - Not configured
                        "Settings": self.firewall_notification.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "settings",
                            "Option": "InboundUserNotification",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicSettingsNotification": {
                        "Policy": "Network firewall: Public: Settings: Display a notification",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No
                        # - Not configured
                        "Settings": self.firewall_notification.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "settings",
                            "Option": "InboundUserNotification",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_notification,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainSettingsLocalFirewallRules": {
                        "Policy": "Network firewall: Domain: Settings: Apply "
                        "local firewall rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "settings",
                            "Option": "LocalFirewallRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateSettingsLocalFirewallRules": {
                        "Policy": "Network firewall: Private: Settings: Apply "
                        "local firewall rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "settings",
                            "Option": "LocalFirewallRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicSettingsLocalFirewallRules": {
                        "Policy": "Network firewall: Public: Settings: Apply "
                        "local firewall rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "settings",
                            "Option": "LocalFirewallRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainSettingsLocalConnectionRules": {
                        "Policy": "Network firewall: Domain: Settings: Apply "
                        "local connection security rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "settings",
                            "Option": "LocalConSecRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateSettingsLocalConnectionRules": {
                        "Policy": "Network firewall: Private: Settings: Apply "
                        "local connection security rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "settings",
                            "Option": "LocalConSecRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicSettingsLocalConnectionRules": {
                        "Policy": "Network firewall: Public: Settings: Apply "
                        "local connection security rules",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes (default)
                        # - No
                        # - Not configured
                        "Settings": self.firewall_rule_merging.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "settings",
                            "Option": "LocalConSecRules",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_rule_merging,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainLoggingName": {
                        "Policy": "Network firewall: Domain: Logging: Name",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <a full path to a file>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "logging",
                            "Option": "FileName",
                        },
                    },
                    "WfwPrivateLoggingName": {
                        "Policy": "Network firewall: Private: Logging: Name",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <a full path to a file>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "private",
                            "Section": "logging",
                            "Option": "FileName",
                        },
                    },
                    "WfwPublicLoggingName": {
                        "Policy": "Network firewall: Public: Logging: Name",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <a full path to a file>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "public",
                            "Section": "logging",
                            "Option": "FileName",
                        },
                    },
                    "WfwDomainLoggingMaxFileSize": {
                        "Policy": "Network firewall: Domain: Logging: Size limit (KB)",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <int between 1 and 32767>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "logging",
                            "Option": "MaxFileSize",
                        },
                    },
                    "WfwPrivateLoggingMaxFileSize": {
                        "Policy": "Network firewall: Private: Logging: Size limit (KB)",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <int between 1 and 32767>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "private",
                            "Section": "logging",
                            "Option": "MaxFileSize",
                        },
                    },
                    "WfwPublicLoggingMaxFileSize": {
                        "Policy": "Network firewall: Public: Logging: Size limit (KB)",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - <int between 1 and 32767>
                        # - Not configured
                        "Settings": None,
                        "NetSH": {
                            "Profile": "public",
                            "Section": "logging",
                            "Option": "MaxFileSize",
                        },
                    },
                    "WfwDomainLoggingAllowedConnections": {
                        "Policy": "Network firewall: Domain: Logging: Log successful connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "logging",
                            "Option": "LogAllowedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateLoggingAllowedConnections": {
                        "Policy": "Network firewall: Private: Logging: Log successful connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "logging",
                            "Option": "LogAllowedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicLoggingAllowedConnections": {
                        "Policy": "Network firewall: Public: Logging: Log successful connections",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "logging",
                            "Option": "LogAllowedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwDomainLoggingDroppedConnections": {
                        "Policy": "Network firewall: Domain: Logging: Log dropped packets",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "domain",
                            "Section": "logging",
                            "Option": "LogDroppedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPrivateLoggingDroppedConnections": {
                        "Policy": "Network firewall: Private: Logging: Log dropped packets",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "private",
                            "Section": "logging",
                            "Option": "LogDroppedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "WfwPublicLoggingDroppedConnections": {
                        "Policy": "Network firewall: Public: Logging: Log dropped packets",
                        "lgpo_section": self.windows_firewall_gpedit_path,
                        # Settings available are:
                        # - Yes
                        # - No (default)
                        # - Not configured
                        "Settings": self.firewall_log_packets_connections.keys(),
                        "NetSH": {
                            "Profile": "public",
                            "Section": "logging",
                            "Option": "LogDroppedConnections",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.firewall_log_packets_connections,
                                "value_lookup": True,
                            },
                        },
                    },
                    "PasswordHistory": {
                        "Policy": "Enforce password history",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 24},
                        },
                        "NetUserModal": {"Modal": 0, "Option": "password_hist_len"},
                    },
                    "MaxPasswordAge": {
                        "Policy": "Maximum password age",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {
                                "min": 1,
                                "max": 86313600,
                                "zero_value": 0xFFFFFFFF,
                            },
                        },
                        "NetUserModal": {"Modal": 0, "Option": "max_passwd_age"},
                        "Transform": {
                            "Get": "_seconds_to_days",
                            "Put": "_days_to_seconds",
                            "GetArgs": {"zero_value": 0xFFFFFFFF},
                            "PutArgs": {"zero_value": 0xFFFFFFFF},
                        },
                    },
                    "MinPasswordAge": {
                        "Policy": "Minimum password age",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 86313600},
                        },
                        "NetUserModal": {"Modal": 0, "Option": "min_passwd_age"},
                        "Transform": {
                            "Get": "_seconds_to_days",
                            "Put": "_days_to_seconds",
                        },
                    },
                    "MinPasswordLen": {
                        "Policy": "Minimum password length",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 14},
                        },
                        "NetUserModal": {"Modal": 0, "Option": "min_passwd_len"},
                    },
                    "PasswordComplexity": {
                        "Policy": "Password must meet complexity requirements",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "Secedit": {
                            "Option": "PasswordComplexity",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "ClearTextPasswords": {
                        "Policy": "Store passwords using reversible encryption",
                        "lgpo_section": self.password_policy_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "Secedit": {
                            "Option": "ClearTextPassword",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "AdminAccountStatus": {
                        "Policy": "Accounts: Administrator account status",
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Secedit": {
                            "Option": "EnableAdminAccount",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "NoConnectedUser": {
                        "Policy": "Accounts: Block Microsoft accounts",
                        "Settings": self.block_ms_accounts.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "NoConnectedUser",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.block_ms_accounts,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.block_ms_accounts,
                                "value_lookup": True,
                            },
                        },
                    },
                    "GuestAccountStatus": {
                        "Policy": "Accounts: Guest account status",
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Secedit": {
                            "Option": "EnableGuestAccount",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "LimitBlankPasswordUse": {
                        "Policy": "Accounts: Limit local account use of blank "
                        "passwords to console logon only",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "limitblankpassworduse",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "RenameAdministratorAccount": {
                        "Policy": "Accounts: Rename administrator account",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Secedit": {
                            "Option": "NewAdministratorName",
                            "Section": "System Access",
                        },
                        "Transform": {"Get": "_strip_quotes", "Put": "_add_quotes"},
                    },
                    "RenameGuestAccount": {
                        "Policy": "Accounts: Rename guest account",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Secedit": {
                            "Option": "NewGuestName",
                            "Section": "System Access",
                        },
                        "Transform": {"Get": "_strip_quotes", "Put": "_add_quotes"},
                    },
                    "AuditBaseObjects": {
                        "Policy": "Audit: Audit the access of global system " "objects",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "AuditBaseObjects",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "SceNoApplyLegacyAuditPolicy": {
                        "Policy": "Audit: Force audit policy subcategory "
                        "settings (Windows Vista or later) to "
                        "override audit policy category settings",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "AuditBaseObjects",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "DontDisplayLastUserName": {
                        "Policy": "Interactive logon: Do not display last user " "name",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "DontDisplayLastUserName",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "CachedLogonsCount": {
                        "Policy": "Interactive logon: Number of previous "
                        "logons to cache (in case domain controller "
                        "is not available)",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 50},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "CachedLogonsCount",
                            "Type": "REG_SZ",
                        },
                    },
                    "ForceUnlockLogon": {
                        "Policy": "Interactive logon: Require Domain "
                        "Controller authentication to unlock "
                        "workstation",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "ForceUnlockLogon",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ScRemoveOption": {
                        "Policy": "Interactive logon: Smart card removal " "behavior",
                        "Settings": self.sc_removal_lookup.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "ScRemoveOption",
                            "Type": "REG_SZ",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.sc_removal_lookup,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.sc_removal_lookup,
                                "value_lookup": True,
                            },
                        },
                    },
                    "DisableCAD": {
                        "Policy": "Interactive logon: Do not require " "CTRL+ALT+DEL",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "DisableCAD",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "FilterAdministratorToken": {
                        "Policy": "User Account Control: Admin Approval Mode "
                        "for the built-in Administrator account",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "FilterAdministratorToken",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnableUIADesktopToggle": {
                        "Policy": "User Account Control: Allow UIAccess "
                        "applications to prompt for elevation "
                        "without using the secure desktop",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "EnableUIADesktopToggle",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ConsentPromptBehaviorAdmin": {
                        "Policy": "User Account Control: Behavior of the "
                        "elevation prompt for administrators in "
                        "Admin Approval Mode",
                        "Settings": self.uac_admin_prompt_lookup.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "ConsentPromptBehaviorAdmin",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.uac_admin_prompt_lookup,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.uac_admin_prompt_lookup,
                                "value_lookup": True,
                            },
                        },
                    },
                    "ConsentPromptBehaviorUser": {
                        "Policy": "User Account Control: Behavior of the "
                        "elevation prompt for standard users",
                        "Settings": self.uac_user_prompt_lookup.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "ConsentPromptBehaviorUser",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.uac_user_prompt_lookup,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.uac_user_prompt_lookup,
                                "value_lookup": True,
                            },
                        },
                    },
                    "EnableInstallerDetection": {
                        "Policy": "User Account Control: Detect application "
                        "installations and prompt for elevation",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "EnableInstallerDetection",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ValidateAdminCodeSignatures": {
                        "Policy": "User Account Control: Only elevate "
                        "executables that are signed and validated",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "ValidateAdminCodeSignatures",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnableSecureUIAPaths": {
                        "Policy": "User Account Control: Only elevate UIAccess "
                        "applications that are installed in secure "
                        "locations",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "EnableSecureUIAPaths",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnableLUA": {
                        "Policy": "User Account Control: Run all "
                        "administrators in Admin Approval Mode",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "EnableLUA",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "PromptOnSecureDesktop": {
                        "Policy": "User Account Control: Switch to the secure "
                        "desktop when prompting for elevation",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "PromptOnSecureDesktop",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnableVirtualization": {
                        "Policy": "User Account Control: Virtualize file and "
                        "registry write failures to per-user "
                        "locations",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "EnableVirtualization",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "PasswordExpiryWarning": {
                        "Policy": "Interactive logon: Prompt user to change "
                        "password before expiration",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 999},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "PasswordExpiryWarning",
                            "Type": "REG_DWORD",
                        },
                    },
                    "MaxDevicePasswordFailedAttempts": {
                        "Policy": "Interactive logon: Machine account lockout "
                        "threshold",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 999},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "MaxDevicePasswordFailedAttempts",
                            "Type": "REG_DWORD",
                        },
                    },
                    "InactivityTimeoutSecs": {
                        "Policy": "Interactive logon: Machine inactivity limit",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 599940},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "InactivityTimeoutSecs",
                            "Type": "REG_DWORD",
                        },
                    },
                    "legalnoticetext": {
                        "Policy": "Interactive logon: Message text for users "
                        "attempting to log on",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "legalnoticetext",
                            "Type": "REG_SZ",
                        },
                        "Transform": {"Put": "_string_put_transform"},
                    },
                    "legalnoticecaption": {
                        "Policy": "Interactive logon: Message title for users "
                        "attempting to log on",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "legalnoticecaption",
                            "Type": "REG_SZ",
                        },
                        "Transform": {"Put": "_string_put_transform"},
                    },
                    "DontDisplayLockedUserId": {
                        "Policy": "Interactive logon: Display user information "
                        "when the session is locked",
                        "Settings": self.locked_session_user_info.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\"
                            "CurrentVersion\\policies\\system",
                            "Value": "DontDisplayLockedUserId",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.locked_session_user_info,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.locked_session_user_info,
                                "value_lookup": True,
                            },
                        },
                    },
                    "ScForceOption": {
                        "Policy": "Interactive logon: Require smart card",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "ScForceOption",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "Client_RequireSecuritySignature": {
                        "Policy": "Microsoft network client: Digitally sign "
                        "communications (always)",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanWorkstation\\Parameters",
                            "Value": "RequireSecuritySignature",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "Client_EnableSecuritySignature": {
                        "Policy": "Microsoft network client: Digitally sign "
                        "communications (if server agrees)",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanWorkstation\\Parameters",
                            "Value": "EnableSecuritySignature",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnablePlainTextPassword": {
                        "Policy": "Microsoft network client: Send unencrypted "
                        "password to third-party SMB servers",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanWorkstation\\Parameters",
                            "Value": "EnablePlainTextPassword",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "AutoDisconnect": {
                        "Policy": "Microsoft network server: Amount of idle "
                        "time required before suspending session",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 99999},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "AutoDisconnect",
                            "Type": "REG_DWORD",
                        },
                    },
                    "EnableS4U2SelfForClaims": {
                        "Policy": "Microsoft network server: Attempt S4U2Self "
                        "to obtain claim information",
                        "Settings": self.s4u2self_options.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "EnableS4U2SelfForClaims",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.s4u2self_options,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.s4u2self_options,
                                "value_lookup": True,
                            },
                        },
                    },
                    "Server_RequireSecuritySignature": {
                        "Policy": "Microsoft network server: Digitally sign "
                        "communications (always)",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "RequireSecuritySignature",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "Server_EnableSecuritySignature": {
                        "Policy": "Microsoft network server: Digitally sign "
                        "communications (if client agrees)",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "EnableSecuritySignature",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "EnableForcedLogoff": {
                        "Policy": "Microsoft network server: Disconnect "
                        "clients when logon hours expire",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "EnableForcedLogoff",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "SmbServerNameHardeningLevel": {
                        "Policy": "Microsoft network server: Server SPN target "
                        "name validation level",
                        "Settings": self.smb_server_name_hardening_levels.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "LanmanServer\\Parameters",
                            "Value": "SmbServerNameHardeningLevel",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.smb_server_name_hardening_levels,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.smb_server_name_hardening_levels,
                                "value_lookup": True,
                            },
                        },
                    },
                    "FullPrivilegeAuditing": {
                        "Policy": "Audit: Audit the use of Backup and Restore "
                        "privilege",
                        "Settings": [chr(0), chr(1)],
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa",
                            "Value": "FullPrivilegeAuditing",
                            "Type": "REG_BINARY",
                        },
                        "Transform": {
                            "Get": "_binary_enable_zero_disable_one_conversion",
                            "Put": "_binary_enable_zero_disable_one_reverse_conversion",
                        },
                    },
                    "CrashOnAuditFail": {
                        "Policy": "Audit: Shut down system immediately if "
                        "unable to log security audits",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "CrashOnAuditFail",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "UndockWithoutLogon": {
                        "Policy": "Devices: Allow undock without having to log " "on",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows\\"
                            "CurrentVersion\\Policies\\System",
                            "Value": "UndockWithoutLogon",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "AddPrinterDrivers": {
                        "Policy": "Devices: Prevent users from installing "
                        "printer drivers",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\"
                            "Print\\Providers\\LanMan Print Services\\"
                            "Servers",
                            "Value": "AddPrinterDrivers",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "AllocateDASD": {
                        "Policy": "Devices: Allowed to format and eject "
                        "removable media",
                        "Settings": ["9999", "0", "1", "2"],
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "AllocateDASD",
                            "Type": "REG_SZ",
                        },
                        "Transform": {
                            "Get": "_dasd_conversion",
                            "Put": "_dasd_reverse_conversion",
                        },
                    },
                    "AllocateCDRoms": {
                        "Policy": "Devices: Restrict CD-ROM access to locally "
                        "logged-on user only",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "AllocateCDRoms",
                            "Type": "REG_SZ",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "AllocateFloppies": {
                        "Policy": "Devices: Restrict floppy access to locally "
                        "logged-on user only",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Winlogon",
                            "Value": "AllocateFloppies",
                            "Type": "REG_SZ",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    # see KB298503 why we aren't just doing this one via the
                    # registry
                    "DriverSigningPolicy": {
                        "Policy": "Devices: Unsigned driver installation " "behavior",
                        "Settings": ["3,0", "3," + chr(1), "3," + chr(2)],
                        "lgpo_section": self.security_options_gpedit_path,
                        "Secedit": {
                            "Option": "MACHINE\\Software\\Microsoft\\Driver "
                            "Signing\\Policy",
                            "Section": "Registry Values",
                        },
                        "Transform": {
                            "Get": "_driver_signing_reg_conversion",
                            "Put": "_driver_signing_reg_reverse_conversion",
                        },
                    },
                    "SubmitControl": {
                        "Policy": "Domain controller: Allow server operators "
                        "to schedule tasks",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa",
                            "Value": "SubmitControl",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "LDAPServerIntegrity": {
                        "Policy": "Domain controller: LDAP server signing "
                        "requirements",
                        "Settings": self.ldap_server_signing_requirements.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\NTDS"
                            "\\Parameters",
                            "Value": "LDAPServerIntegrity",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.ldap_server_signing_requirements,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ldap_server_signing_requirements,
                                "value_lookup": True,
                            },
                        },
                    },
                    "RefusePasswordChange": {
                        "Policy": "Domain controller: Refuse machine account "
                        "password changes",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "RefusePasswordChange",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "RequireSignOrSeal": {
                        "Policy": "Domain member: Digitally encrypt or sign "
                        "secure channel data (always)",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "RequireSignOrSeal",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "SealSecureChannel": {
                        "Policy": "Domain member: Digitally encrypt secure "
                        "channel data (when possible)",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "SealSecureChannel",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "SignSecureChannel": {
                        "Policy": "Domain member: Digitally sign secure "
                        "channel data (when possible)",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "SignSecureChannel",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "DisablePasswordChange": {
                        "Policy": "Domain member: Disable machine account "
                        "password changes",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "DisablePasswordChange",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "MaximumPasswordAge": {
                        "Policy": "Domain member: Maximum machine account "
                        "password age",
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 999},
                        },
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "MaximumPasswordAge",
                            "Type": "REG_DWORD",
                        },
                    },
                    "RequireStrongKey": {
                        "Policy": "Domain member: Require strong (Windows 2000 "
                        "or later) session key",
                        "Settings": self.enabled_one_disabled_zero_strings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\"
                            "Netlogon\\Parameters",
                            "Value": "RequireStrongKey",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_strings_transform,
                    },
                    "LockoutDuration": {
                        "Policy": "Account lockout duration",
                        "lgpo_section": self.account_lockout_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 6000000},
                        },
                        "NetUserModal": {"Modal": 3, "Option": "lockout_duration"},
                        "Transform": {
                            "Get": "_seconds_to_minutes",
                            "Put": "_minutes_to_seconds",
                        },
                    },
                    "LockoutThreshold": {
                        "Policy": "Account lockout threshold",
                        "lgpo_section": self.account_lockout_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 1000},
                        },
                        "NetUserModal": {"Modal": 3, "Option": "lockout_threshold"},
                    },
                    "LockoutWindow": {
                        "Policy": "Reset account lockout counter after",
                        "lgpo_section": self.account_lockout_policy_gpedit_path,
                        "Settings": {
                            "Function": "_in_range_inclusive",
                            "Args": {"min": 0, "max": 6000000},
                        },
                        "NetUserModal": {
                            "Modal": 3,
                            "Option": "lockout_observation_window",
                        },
                        "Transform": {
                            "Get": "_seconds_to_minutes",
                            "Put": "_minutes_to_seconds",
                        },
                    },
                    ########## LEGACY AUDIT POLICIES ##########
                    # To use these set the following policy to DISABLED
                    # "Audit: Force audit policy subcategory settings (Windows Vista or later) to override audit policy category settings"
                    # or it's alias...
                    # SceNoApplyLegacyAuditPolicy
                    "AuditAccountLogon": {
                        "Policy": "Audit account logon events",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditAccountLogon",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditAccountManage": {
                        "Policy": "Audit account management",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditAccountManage",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditDSAccess": {
                        "Policy": "Audit directory service access",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditDSAccess",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditLogonEvents": {
                        "Policy": "Audit logon events",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditLogonEvents",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditObjectAccess": {
                        "Policy": "Audit object access",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditObjectAccess",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditPolicyChange": {
                        "Policy": "Audit policy change",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditPolicyChange",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditPrivilegeUse": {
                        "Policy": "Audit privilege use",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditPrivilegeUse",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditProcessTracking": {
                        "Policy": "Audit process tracking",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditProcessTracking",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    "AuditSystemEvents": {
                        "Policy": "Audit system events",
                        "lgpo_section": self.audit_policy_gpedit_path,
                        "Settings": self.audit_lookup.keys(),
                        "Secedit": {
                            "Option": "AuditSystemEvents",
                            "Section": "Event Audit",
                        },
                        "Transform": self.audit_transform,
                    },
                    ########## END OF LEGACY AUDIT POLICIES ##########
                    ########## ADVANCED AUDIT POLICIES ##########
                    # Advanced Audit Policies
                    # To use these set the following policy to ENABLED
                    # "Audit: Force audit policy subcategory settings (Windows
                    # Vista or later) to override audit policy category
                    # settings"
                    # or it's alias...
                    # SceNoApplyLegacyAuditPolicy
                    # Account Logon Section
                    "AuditCredentialValidation": {
                        "Policy": "Audit Credential Validation",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Credential Validation"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditKerberosAuthenticationService": {
                        "Policy": "Audit Kerberos Authentication Service",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit Kerberos Authentication Service",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditKerberosServiceTicketOperations": {
                        "Policy": "Audit Kerberos Service Ticket Operations",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit Kerberos Service Ticket Operations",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherAccountLogonEvents": {
                        "Policy": "Audit Other Account Logon Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other Account Logon Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Account Management Section
                    "AuditApplicationGroupManagement": {
                        "Policy": "Audit Application Group Management",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Application Group Management"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditComputerAccountManagement": {
                        "Policy": "Audit Computer Account Management",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Computer Account Management"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditDistributionGroupManagement": {
                        "Policy": "Audit Distribution Group Management",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Distribution Group Management"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherAccountManagementEvents": {
                        "Policy": "Audit Other Account Management Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit Other Account Management Events",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSecurityGroupManagement": {
                        "Policy": "Audit Security Group Management",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Security Group Management"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditUserAccountManagement": {
                        "Policy": "Audit User Account Management",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit User Account Management"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Detailed Tracking Settings
                    "AuditDPAPIActivity": {
                        "Policy": "Audit DPAPI Activity",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit DPAPI Activity"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditPNPActivity": {
                        "Policy": "Audit PNP Activity",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit PNP Activity"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditProcessCreation": {
                        "Policy": "Audit Process Creation",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Process Creation"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditProcessTermination": {
                        "Policy": "Audit Process Termination",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Process Termination"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditRPCEvents": {
                        "Policy": "Audit RPC Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit RPC Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditTokenRightAdjusted": {
                        "Policy": "Audit Token Right Adjusted",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Token Right Adjusted"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # DS Access Section
                    "AuditDetailedDirectoryServiceReplication": {
                        "Policy": "Audit Detailed Directory Service Replication",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit Detailed Directory Service Replication",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditDirectoryServiceAccess": {
                        "Policy": "Audit Directory Service Access",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Directory Service Access"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditDirectoryServiceChanges": {
                        "Policy": "Audit Directory Service Changes",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Directory Service Changes"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditDirectoryServiceReplication": {
                        "Policy": "Audit Directory Service Replication",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Directory Service Replication"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Logon/Logoff Section
                    "AuditAccountLockout": {
                        "Policy": "Audit Account Lockout",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Account Lockout"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditUserDeviceClaims": {
                        "Policy": "Audit User / Device Claims",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit User / Device Claims"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditGroupMembership": {
                        "Policy": "Audit Group Membership",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Group Membership"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditIPsecExtendedMode": {
                        "Policy": "Audit IPsec Extended Mode",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit IPsec Extended Mode"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditIPsecMainMode": {
                        "Policy": "Audit IPsec Main Mode",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit IPsec Main Mode"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditIPsecQuickMode": {
                        "Policy": "Audit IPsec Quick Mode",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit IPsec Quick Mode"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditLogoff": {
                        "Policy": "Audit Logoff",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Logoff"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditLogon": {
                        "Policy": "Audit Logon",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Logon"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditNetworkPolicyServer": {
                        "Policy": "Audit Network Policy Server",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Network Policy Server"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherLogonLogoffEvents": {
                        "Policy": "Audit Other Logon/Logoff Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other Logon/Logoff Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSpecialLogon": {
                        "Policy": "Audit Special Logon",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Special Logon"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Object Access Section
                    "AuditApplicationGenerated": {
                        "Policy": "Audit Application Generated",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Application Generated"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditCertificationServices": {
                        "Policy": "Audit Certification Services",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Certification Services"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditDetailedFileShare": {
                        "Policy": "Audit Detailed File Share",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Detailed File Share"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditFileShare": {
                        "Policy": "Audit File Share",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit File Share"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditFileSystem": {
                        "Policy": "Audit File System",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit File System"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditFilteringPlatformConnection": {
                        "Policy": "Audit Filtering Platform Connection",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Filtering Platform Connection"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditFilteringPlatformPacketDrop": {
                        "Policy": "Audit Filtering Platform Packet Drop",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Filtering Platform Packet Drop"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditHandleManipulation": {
                        "Policy": "Audit Handle Manipulation",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Handle Manipulation"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditKernelObject": {
                        "Policy": "Audit Kernel Object",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Kernel Object"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherObjectAccessEvents": {
                        "Policy": "Audit Other Object Access Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other Object Access Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditRegistry": {
                        "Policy": "Audit Registry",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Registry"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditRemovableStorage": {
                        "Policy": "Audit Removable Storage",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Removable Storage"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSAM": {
                        "Policy": "Audit SAM",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit SAM"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditCentralAccessPolicyStaging": {
                        "Policy": "Audit Central Access Policy Staging",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Central Access Policy Staging"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Policy Change Section
                    "AuditAuditPolicyChange": {
                        "Policy": "Audit Audit Policy Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Audit Policy Change"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditAuthenticationPolicyChange": {
                        "Policy": "Audit Authentication Policy Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Authentication Policy Change"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditAuthorizationPolicyChange": {
                        "Policy": "Audit Authorization Policy Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Authorization Policy Change"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditFilteringPlatformPolicyChange": {
                        "Policy": "Audit Filtering Platform Policy Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit Filtering Platform Policy Change",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditMPSSVCRuleLevelPolicyChange": {
                        "Policy": "Audit MPSSVC Rule-Level Policy Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {
                            "Option": "Audit MPSSVC Rule-Level Policy Change",
                        },
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherPolicyChangeEvents": {
                        "Policy": "Audit Other Policy Change Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other Policy Change Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # Privilege Use Section
                    "AuditNonSensitivePrivilegeUse": {
                        "Policy": "Audit Non Sensitive Privilege Use",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Non Sensitive Privilege Use"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherPrivilegeUseEvents": {
                        "Policy": "Audit Other Privilege Use Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other Privilege Use Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSensitivePrivilegeUse": {
                        "Policy": "Audit Sensitive Privilege Use",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Sensitive Privilege Use"},
                        "Transform": self.advanced_audit_transform,
                    },
                    # System Section
                    "AuditIPsecDriver": {
                        "Policy": "Audit IPsec Driver",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit IPsec Driver"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditOtherSystemEvents": {
                        "Policy": "Audit Other System Events",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Other System Events"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSecurityStateChange": {
                        "Policy": "Audit Security State Change",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Security State Change"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSecuritySystemExtension": {
                        "Policy": "Audit Security System Extension",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit Security System Extension"},
                        "Transform": self.advanced_audit_transform,
                    },
                    "AuditSystemIntegrity": {
                        "Policy": "Audit System Integrity",
                        "lgpo_section": self.advanced_audit_policy_gpedit_path,
                        "Settings": self.advanced_audit_lookup.keys(),
                        "AdvAudit": {"Option": "Audit System Integrity"},
                        "Transform": self.advanced_audit_transform,
                    },
                    ########## END OF ADVANCED AUDIT POLICIES ##########
                    "SeTrustedCredManAccessPrivilege": {
                        "Policy": "Access Credential Manager as a trusted " "caller",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeTrustedCredManAccessPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeNetworkLogonRight": {
                        "Policy": "Access this computer from the network",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeNetworkLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeTcbPrivilege": {
                        "Policy": "Act as part of the operating system",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeTcbPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeMachineAccountPrivilege": {
                        "Policy": "Add workstations to domain",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeMachineAccountPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeIncreaseQuotaPrivilege": {
                        "Policy": "Adjust memory quotas for a process",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeIncreaseQuotaPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeInteractiveLogonRight": {
                        "Policy": "Allow log on locally",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeInteractiveLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeRemoteInteractiveLogonRight": {
                        "Policy": "Allow log on through Remote Desktop Services",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeRemoteInteractiveLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeBackupPrivilege": {
                        "Policy": "Backup files and directories",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeBackupPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeChangeNotifyPrivilege": {
                        "Policy": "Bypass traverse checking",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeChangeNotifyPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeSystemtimePrivilege": {
                        "Policy": "Change the system time",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeSystemtimePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeTimeZonePrivilege": {
                        "Policy": "Change the time zone",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeTimeZonePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeCreatePagefilePrivilege": {
                        "Policy": "Create a pagefile",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeCreatePagefilePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeCreateTokenPrivilege": {
                        "Policy": "Create a token object",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeCreateTokenPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeCreateGlobalPrivilege": {
                        "Policy": "Create global objects",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeCreateGlobalPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeCreatePermanentPrivilege": {
                        "Policy": "Create permanent shared objects",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeCreatePermanentPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeCreateSymbolicLinkPrivilege": {
                        "Policy": "Create symbolic links",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeCreateSymbolicLinkPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDebugPrivilege": {
                        "Policy": "Debug programs",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDebugPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDenyNetworkLogonRight": {
                        "Policy": "Deny access to this computer from the " "network",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDenyNetworkLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDenyBatchLogonRight": {
                        "Policy": "Deny log on as a batch job",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDenyBatchLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDenyServiceLogonRight": {
                        "Policy": "Deny log on as a service",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDenyServiceLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDenyInteractiveLogonRight": {
                        "Policy": "Deny log on locally",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDenyInteractiveLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeDenyRemoteInteractiveLogonRight": {
                        "Policy": "Deny log on through Remote Desktop Services",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeDenyRemoteInteractiveLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeEnableDelegationPrivilege": {
                        "Policy": "Enable computer and user accounts to be "
                        "trusted for delegation",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeEnableDelegationPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeRemoteShutdownPrivilege": {
                        "Policy": "Force shutdown from a remote system",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeRemoteShutdownPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeAuditPrivilege": {
                        "Policy": "Generate security audits",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeAuditPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeImpersonatePrivilege": {
                        "Policy": "Impersonate a client after authentication",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeImpersonatePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeIncreaseWorkingSetPrivilege": {
                        "Policy": "Increase a process working set",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeIncreaseWorkingSetPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeIncreaseBasePriorityPrivilege": {
                        "Policy": "Increase scheduling priority",
                        "rights_assignment": True,
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "Settings": None,
                        "LsaRights": {"Option": "SeIncreaseBasePriorityPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeLoadDriverPrivilege": {
                        "Policy": "Load and unload device drivers",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeLoadDriverPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeLockMemoryPrivilege": {
                        "Policy": "Lock pages in memory",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeLockMemoryPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeBatchLogonRight": {
                        "Policy": "Log on as a batch job",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeBatchLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeServiceLogonRight": {
                        "Policy": "Log on as a service",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeServiceLogonRight"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeSecurityPrivilege": {
                        "Policy": "Manage auditing and security log",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeSecurityPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeRelabelPrivilege": {
                        "Policy": "Modify an object label",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeRelabelPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeSystemEnvironmentPrivilege": {
                        "Policy": "Modify firmware environment values",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeSystemEnvironmentPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeManageVolumePrivilege": {
                        "Policy": "Perform volume maintenance tasks",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeManageVolumePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeProfileSingleProcessPrivilege": {
                        "Policy": "Profile single process",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeProfileSingleProcessPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeSystemProfilePrivilege": {
                        "Policy": "Profile system performance",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeSystemProfilePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeUndockPrivilege": {
                        "Policy": "Remove computer from docking station",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeUndockPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeAssignPrimaryTokenPrivilege": {
                        "Policy": "Replace a process level token",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeAssignPrimaryTokenPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeRestorePrivilege": {
                        "Policy": "Restore files and directories",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeRestorePrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeShutdownPrivilege": {
                        "Policy": "Shut down the system",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeShutdownPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeSyncAgentPrivilege": {
                        "Policy": "Synchronize directory service data",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeSyncAgentPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "SeTakeOwnershipPrivilege": {
                        "Policy": "Take ownership of files or other objects",
                        "lgpo_section": self.user_rights_assignment_gpedit_path,
                        "rights_assignment": True,
                        "Settings": None,
                        "LsaRights": {"Option": "SeTakeOwnershipPrivilege"},
                        "Transform": {
                            "Get": "_sidConversion",
                            "Put": "_usernamesToSidObjects",
                        },
                    },
                    "RecoveryConsoleSecurityLevel": {
                        "Policy": "Recovery console: Allow automatic "
                        "administrative logon",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Setup\\RecoveryConsole",
                            "Value": "SecurityLevel",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "RecoveryConsoleSetCommand": {
                        "Policy": "Recovery console: Allow floppy copy and "
                        "access to all drives and all folders",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Microsoft\\Windows NT\\"
                            "CurrentVersion\\Setup\\RecoveryConsole",
                            "Value": "SetCommand",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ForceKeyProtection": {
                        "Policy": "System Cryptography: Force strong key protection for "
                        "user keys stored on the computer",
                        "Settings": self.force_key_protection.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Policies\\Microsoft\\Cryptography",
                            "Value": "ForceKeyProtection",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.force_key_protection,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.force_key_protection,
                                "value_lookup": True,
                            },
                        },
                    },
                    "FIPSAlgorithmPolicy": {
                        "Policy": "System Cryptography: Use FIPS compliant algorithms "
                        "for encryption, hashing, and signing",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa\\FIPSAlgorithmPolicy",
                            "Value": "Enabled",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "MachineAccessRestriction": {
                        "Policy": "DCOM: Machine Access Restrictions in Security Descriptor "
                        "Definition Language (SDDL) syntax",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Policies\\Microsoft\\Windows NT\\DCOM",
                            "Value": "MachineAccessRestriction",
                            "Type": "REG_SZ",
                        },
                        "Transform": {"Put": "_string_put_transform"},
                    },
                    "MachineLaunchRestriction": {
                        "Policy": "DCOM: Machine Launch Restrictions in Security Descriptor "
                        "Definition Language (SDDL) syntax",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "Software\\Policies\\Microsoft\\Windows NT\\DCOM",
                            "Value": "MachineLaunchRestriction",
                            "Type": "REG_SZ",
                        },
                        "Transform": {"Put": "_string_put_transform"},
                    },
                    "UseMachineId": {
                        "Policy": "Network security: Allow Local System to use computer "
                        "identity for NTLM",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "UseMachineId",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "allownullsessionfallback": {
                        "Policy": "Network security: Allow LocalSystem NULL session fallback",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0",
                            "Value": "allownullsessionfallback",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "AllowOnlineID": {
                        "Policy": "Network security: Allow PKU2U authentication requests "
                        "to this computer to use online identities.",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa\\pku2u",
                            "Value": "AllowOnlineID",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "KrbSupportedEncryptionTypes": {
                        "Policy": "Network security: Configure encryption types allowed "
                        "for Kerberos",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\policies"
                            "\\system\\Kerberos\\Parameters",
                            "Value": "SupportedEncryptionTypes",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup_bitwise_add",
                            "Put": "_dict_lookup_bitwise_add",
                            "GetArgs": {
                                "lookup": self.krb_encryption_types,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.krb_encryption_types,
                                "value_lookup": True,
                            },
                        },
                    },
                    "NoLMHash": {
                        "Policy": "Network security: Do not store LAN Manager hash value "
                        "on next password change",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "NoLMHash",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ForceLogoffWhenHourExpire": {
                        "Policy": "Network security: Force logoff when logon hours expire",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Settings": self.enabled_one_disabled_zero_no_not_defined.keys(),
                        "Secedit": {
                            "Option": "ForceLogoffWhenHourExpire",
                            "Section": "System Access",
                        },
                        "Transform": self.enabled_one_disabled_zero_no_not_defined_transform,
                    },
                    "LmCompatibilityLevel": {
                        "Policy": "Network security: LAN Manager authentication level",
                        "Settings": self.lm_compat_levels.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa",
                            "Value": "LmCompatibilityLevel",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.lm_compat_levels,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.lm_compat_levels,
                                "value_lookup": True,
                            },
                        },
                    },
                    "LDAPClientIntegrity": {
                        "Policy": "Network security: LDAP client signing requirements",
                        "Settings": self.ldap_signing_reqs.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\ldap",
                            "Value": "LDAPClientIntegrity",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.ldap_signing_reqs,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ldap_signing_reqs,
                                "value_lookup": True,
                            },
                        },
                    },
                    "NTLMMinClientSec": {
                        "Policy": "Network security: Minimum session security for NTLM SSP based "
                        "(including secure RPC) clients",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa\\MSV1_0",
                            "Value": "NTLMMinClientSec",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup_bitwise_add",
                            "Put": "_dict_lookup_bitwise_add",
                            "GetArgs": {
                                "lookup": self.ntlm_session_security_levels,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ntlm_session_security_levels,
                                "value_lookup": True,
                            },
                        },
                    },
                    "NTLMMinServerSec": {
                        "Policy": "Network security: Minimum session security for NTLM SSP based "
                        "(including secure RPC) servers",
                        "Settings": None,
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa\\MSV1_0",
                            "Value": "NTLMMinServerSec",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup_bitwise_add",
                            "Put": "_dict_lookup_bitwise_add",
                            "GetArgs": {
                                "lookup": self.ntlm_session_security_levels,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ntlm_session_security_levels,
                                "value_lookup": True,
                            },
                        },
                    },
                    "ClientAllowedNTLMServers": {
                        "Policy": "Network security: Restrict NTLM: Add remote server"
                        " exceptions for NTLM authentication",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\Lsa\\MSV1_0",
                            "Value": "ClientAllowedNTLMServers",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "DCAllowedNTLMServers": {
                        "Policy": "Network security: Restrict NTLM: Add server exceptions"
                        " in this domain",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Services\\Netlogon\\Parameters",
                            "Value": "DCAllowedNTLMServers",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "AuditReceivingNTLMTraffic": {
                        "Policy": "Network security: Restrict NTLM: Audit Incoming NTLM Traffic",
                        "Settings": self.ntlm_audit_settings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\LSA\\MSV1_0",
                            "Value": "AuditReceivingNTLMTraffic",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.ntlm_audit_settings,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ntlm_audit_settings,
                                "value_lookup": True,
                            },
                        },
                    },
                    "AuditNTLMInDomain": {
                        "Policy": "Network security: Restrict NTLM: Audit NTLM "
                        "authentication in this domain",
                        "Settings": self.ntlm_domain_audit_settings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters",
                            "Value": "AuditNTLMInDomain",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.ntlm_domain_audit_settings,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ntlm_domain_audit_settings,
                                "value_lookup": True,
                            },
                        },
                    },
                    "RestrictReceivingNTLMTraffic": {
                        "Policy": "Network security: Restrict NTLM: Incoming"
                        " NTLM traffic",
                        "Settings": self.incoming_ntlm_settings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\LSA\\MSV1_0",
                            "Value": "RestrictReceivingNTLMTraffic",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.incoming_ntlm_settings,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.incoming_ntlm_settings,
                                "value_lookup": True,
                            },
                        },
                    },
                    "RestrictNTLMInDomain": {
                        "Policy": "Network security: Restrict NTLM: NTLM "
                        "authentication in this domain",
                        "Settings": self.ntlm_domain_auth_settings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Services\\Netlogon\\Parameters",
                            "Value": "RestrictNTLMInDomain",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.ntlm_domain_auth_settings,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.ntlm_domain_auth_settings,
                                "value_lookup": True,
                            },
                        },
                    },
                    "RestrictSendingNTLMTraffic": {
                        "Policy": "Network security: Restrict NTLM: Outgoing NTLM"
                        " traffic to remote servers",
                        "Settings": self.outgoing_ntlm_settings.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SYSTEM\\CurrentControlSet\\Control\\Lsa\\MSV1_0",
                            "Value": "RestrictSendingNTLMTraffic",
                            "Type": "REG_DWORD",
                        },
                        "Transform": {
                            "Get": "_dict_lookup",
                            "Put": "_dict_lookup",
                            "GetArgs": {
                                "lookup": self.outgoing_ntlm_settings,
                                "value_lookup": False,
                            },
                            "PutArgs": {
                                "lookup": self.outgoing_ntlm_settings,
                                "value_lookup": True,
                            },
                        },
                    },
                    "ShutdownWithoutLogon": {
                        "Policy": "Shutdown: Allow system to be shut down "
                        "without having to log on",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\policies\\system",
                            "Value": "ShutdownWithoutLogon",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ClearPageFileAtShutdown": {
                        "Policy": "Shutdown: Clear virtual memory pagefile",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\"
                            "SESSION MANAGER\\MEMORY MANAGEMENT",
                            "Value": "ClearPageFileAtShutdown",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ObCaseInsensitive": {
                        "Policy": "System objects: Require case insensitivity for "
                        "non-Windows subsystems",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\"
                            "SESSION MANAGER\\Kernel",
                            "Value": "ObCaseInsensitive",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "ProtectionMode": {
                        "Policy": "System objects: Strengthen default permissions of "
                        "internal system objects (e.g. Symbolic Links)",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\"
                            "SESSION MANAGER",
                            "Value": "ProtectionMode",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                    "OptionalSubsystems": {
                        "Policy": "System settings: Optional subsystems",
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "System\\CurrentControlSet\\Control\\"
                            "SESSION MANAGER\\SubSystems",
                            "Value": "optional",
                            "Type": "REG_MULTI_SZ",
                        },
                        "Transform": {
                            "Put": "_multi_string_put_transform",
                            "Get": "_multi_string_get_transform",
                        },
                    },
                    "AuthenticodeEnabled": {
                        "Policy": "System settings: Use Certificate Rules on Windows"
                        " Executables for Software Restriction Policies",
                        "Settings": self.enabled_one_disabled_zero.keys(),
                        "lgpo_section": self.security_options_gpedit_path,
                        "Registry": {
                            "Hive": "HKEY_LOCAL_MACHINE",
                            "Path": "SOFTWARE\\Policies\\Microsoft\\Windows\\safer\\codeidentifiers",
                            "Value": "AuthenticodeEnabled",
                            "Type": "REG_DWORD",
                        },
                        "Transform": self.enabled_one_disabled_zero_transform,
                    },
                },
            },
            "User": {"lgpo_section": "User Configuration", "policies": {}},
        }
        self.admx_registry_classes = {
            "User": {
                "policy_path": os.path.join(
                    os.getenv("WINDIR"),
                    "System32",
                    "GroupPolicy",
                    "User",
                    "Registry.pol",
                ),
                "hive": "HKEY_USERS",
                "lgpo_section": "User Configuration",
                "gpt_extension_location": "gPCUserExtensionNames",
                "gpt_extension_guid": "[{35378EAC-683F-11D2-A89A-00C04FBBCFA2}{D02B1F73-3407-48AE-BA88-E8213C6761F1}]",
            },
            "Machine": {
                "policy_path": os.path.join(
                    os.getenv("WINDIR"),
                    "System32",
                    "GroupPolicy",
                    "Machine",
                    "Registry.pol",
                ),
                "hive": "HKEY_LOCAL_MACHINE",
                "lgpo_section": "Computer Configuration",
                "gpt_extension_location": "gPCMachineExtensionNames",
                "gpt_extension_guid": "[{35378EAC-683F-11D2-A89A-00C04FBBCFA2}{D02B1F72-3407-48AE-BA88-E8213C6761F1}]",
            },
        }
        self.reg_pol_header = "\u5250\u6765\x01\x00"
        self.gpt_ini_path = os.path.join(
            os.getenv("WINDIR"), "System32", "GroupPolicy", "gpt.ini"
        )