def hardcoded_password_string(context):
    """**B105: Test for use of hard-coded password strings**

    The use of hard-coded passwords increases the possibility of password
    guessing tremendously. This plugin test looks for all string literals and
    checks the following conditions:

    - assigned to a variable that looks like a password
    - assigned to a dict key that looks like a password
    - used in a comparison with a variable that looks like a password

    Variables are considered to look like a password if they have match any one
    of:

    - "password"
    - "pass"
    - "passwd"
    - "pwd"
    - "secret"
    - "token"
    - "secrete"

    Note: this can be noisy and may generate false positives.

    **Config Options:**

    None

    :Example:

    .. code-block:: none

        >> Issue: Possible hardcoded password '(root)'
           Severity: Low   Confidence: Low
           Location: ./examples/hardcoded-passwords.py:5
        4 def someFunction2(password):
        5     if password == "root":
        6         print("OK, logged in")

    .. seealso::

        - https://www.owasp.org/index.php/Use_of_hard-coded_password

    .. versionadded:: 0.9.0

    """
    node = context.node
    if isinstance(node.parent, ast.Assign):
        # looks for "candidate='some_string'"
        for targ in node.parent.targets:
            if isinstance(targ, ast.Name) and RE_CANDIDATES.search(targ.id):
                return _report(node.s)

    elif isinstance(node.parent, ast.Index) and RE_CANDIDATES.search(node.s):
        # looks for "dict[candidate]='some_string'"
        # assign -> subscript -> index -> string
        assign = node.parent.parent.parent
        if isinstance(assign, ast.Assign) and isinstance(assign.value,
                                                         ast.Str):
            return _report(assign.value.s)

    elif isinstance(node.parent, ast.Compare):
        # looks for "candidate == 'some_string'"
        comp = node.parent
        if isinstance(comp.left, ast.Name):
            if RE_CANDIDATES.search(comp.left.id):
                if isinstance(comp.comparators[0], ast.Str):
                    return _report(comp.comparators[0].s)