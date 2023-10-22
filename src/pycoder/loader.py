from importlib.util import spec_from_file_location, module_from_spec
from importlib.abc import Loader
import sys


def load_module_from_path(module_name: str, module_path: str):
    """dynamically import module from module name and file path.
    :param module_name: module name
    :param module_path: module file path
    :return module: imported module
    """
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    sys.modules[module_name] = module

    # This assert statement needed for fix below error with mypy.
    # error message:
    #   error: Item "_Loader" of "Optional[_Loader]" has no attribute "exec_module"
    #   error: Item "None" of "Optional[_Loader]" has no attribute "exec_module"
    # reference link:
    #   https://github.com/python/typeshed/issues/2793
    assert isinstance(spec.loader, Loader)

    spec.loader.exec_module(module)
    return module
