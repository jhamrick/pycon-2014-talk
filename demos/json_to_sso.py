import json
import os
import pickle
import importlib


def import_class(module_name, class_name):
    mod = importlib.import_module(module_name)
    return getattr(mod, class_name)


def unicode_to_str(obj):
    if isinstance(obj, dict):
        obj = {str(k): unicode_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        obj = [unicode_to_str(x) for x in obj]
    elif isinstance(obj, unicode):
        obj = str(obj)

    return obj


sso_paths = []
for dirname, dirnames, filenames in os.walk("stimuli"):
    for filename in filenames:
        if filename.endswith(".json"):
            sso_paths.append(os.path.join(dirname, filename))

for filename in sso_paths:
    sso_name = os.path.splitext(os.path.basename(filename))[0]
    dest = os.path.join(os.path.split(filename)[0], "{}.cpo".format(sso_name))
    print(dest)

    with open(filename, 'r') as fh:
        types, props, porder = json.load(fh)
    types = [import_class(t[0], t[1]) for t in types]
    props = unicode_to_str(props)
    for p in props:
        for prop, val in p.items():
            if isinstance(val, dict) and "__class__" in val:
                cls = import_class(val["__class__"][0], val["__class__"][1])
                p[prop] = cls(*val["value"])

    with open(dest, 'w') as fh:
        pickle.dump([types, props, porder], fh)
