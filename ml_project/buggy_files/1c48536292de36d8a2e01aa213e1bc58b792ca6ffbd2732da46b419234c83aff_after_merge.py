                def detect_ksu_prompt(b_data):
                    return re.match(b"Kerberos password for .*@.*:", b_data)