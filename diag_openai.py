import importlib, sys, site, json
try:
    import importlib.util as importlib_util
except Exception:
    importlib_util = None

print("importlib module file:", getattr(importlib, "__file__", None))
print("importlib available attrs:", [a for a in dir(importlib) if not a.startswith('__')])
print("importlib.util import succeeded:", importlib_util is not None)

def run():
    util = importlib_util or getattr(importlib, 'util', None)
    if util is None:
        spec = None
        spec_origin = None
        found = False
        note = 'importlib.util missing'
    else:
        spec = util.find_spec("openai")
        spec_origin = getattr(spec, "origin", None)
        found = bool(spec)
        note = None

    out = {
        "found": found,
        "spec_origin": spec_origin,
        "importlib_util_present": util is not None,
        "note": note,
        "executable": sys.executable,
        "sys_prefix": sys.prefix,
        "sys_path": sys.path,
        "site_packages": getattr(site, "getsitepackages", lambda: [])(),
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    run()
