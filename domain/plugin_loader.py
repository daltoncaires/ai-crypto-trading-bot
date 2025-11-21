from importlib import import_module
from typing import Any, Optional, Type

from utils.logger import get_logger

logger = get_logger(__name__)

def load_plugin(module_path: str, class_name: str, version: Optional[str] = None) -> Type[Any]:
    """
    Dynamically loads a class from a specified module, with optional versioning.

    Args:
        module_path: The dot-separated path to the module (e.g., "my_package.my_module").
        class_name: The base name of the class to load from the module.
        version: Optional. The version of the class to load (e.g., "v1").
                 If provided, attempts to load 'ClassNameV<version>' first.

    Returns:
        The loaded class type.

    Raises:
        ImportError: If the module or class cannot be found.
    """
    try:
        module = import_module(module_path)

        if version:
            versioned_class_name = f"{class_name}V{version.upper()}"
            try:
                component_class = getattr(module, versioned_class_name)
                logger.info(f"Loaded versioned plugin: {versioned_class_name} from {module_path}")
                return component_class  # type: ignore[no-any-return]
            except AttributeError:
                logger.warning(f"Versioned class {versioned_class_name} not found in {module_path}. Falling back to {class_name}.")

        component_class = getattr(module, class_name)
        logger.info(f"Loaded plugin: {class_name} from {module_path}")
        return component_class  # type: ignore[no-any-return]
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not load plugin '{class_name}' from '{module_path}' (version: {version}): {e}"
        ) from e

