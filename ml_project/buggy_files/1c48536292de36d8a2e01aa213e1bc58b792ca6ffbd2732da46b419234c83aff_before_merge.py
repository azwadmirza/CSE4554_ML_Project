                def detect_ksu_prompt(data):
                    return re.match("Kerberos password for .*@.*:", data)