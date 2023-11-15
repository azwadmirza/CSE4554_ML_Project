def main():
    target_python = TargetPython.python3crystax
    recipes = modified_recipes()
    print('recipes modified:', recipes)
    recipes -= CORE_RECIPES
    print('recipes to build:', recipes)
    context = Context()
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        context, recipes, None)
    # fallback to python2 if default target is not compatible
    if target_python.name not in build_order:
        print('incompatible with {}'.format(target_python.name))
        target_python = TargetPython.python2
        print('falling back to {}'.format(target_python.name))
    # removing the known broken recipe for the given target
    broken_recipes = BROKEN_RECIPES[target_python]
    recipes -= broken_recipes
    print('recipes to build (no broken):', recipes)
    build(target_python, recipes)