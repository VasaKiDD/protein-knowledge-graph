import pickle
from typing import Any, Dict, Tuple

from pybiographs.resources import mapping_files


# TODO(Vasakidd): Make sure all the relevant info is included in the documentation.
class Mappings:
    def __init__(self):
        for name in self.names:
            setattr(self, "_%s" % name, None)

    @property
    def names(self) -> Tuple[str]:
        return mapping_files._fields

    def __getattr__(self, item) -> Dict[str, Any]:
        if item not in self.names:
            raise AttributeError(
                "%s is not a valid mapping. Valid mappings are %s" % (item, self.names)
            )
        under_name = "_%s" % item
        value = getattr(self, under_name)
        if value is None:
            with open(getattr(mapping_files, item), "rb") as f:
                data = pickle.load(f)
                setattr(self, under_name, data)
        return value if value is not None else getattr(self, under_name)
