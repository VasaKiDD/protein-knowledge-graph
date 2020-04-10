import pickle
from typing import Any, Dict, List

import pandas

from pybiographs.resources import covid_files


# TODO(Vasakidd): Make sure all the relevant info is included in the documentation.
class CovidData:
    names = ("df", "dict", "interacting_nodes")

    def __init__(self):
        """Initialize a :class:`CovidData`."""
        self._df = None
        self._dict = None
        self._interacting_nodes = None

    def __getitem__(self, item):
        return self.dict[item]

    def __getattr__(self, item):
        return getattr(self.dict, item)

    @property
    def df(self) -> pandas.DataFrame:
        if self._df is None:
            self._df = pandas.read_csv(covid_files.csv)
        return self._df

    @property
    def dict(self) -> Dict[str, Any]:
        if self._dict is None:
            with open(covid_files.data, "rb") as f:
                self._dict = pickle.load(f)
        return self._dict

    @property
    def interacting_nodes(self) -> List[str]:
        if self._interacting_nodes is None:
            with open(covid_files.data, "rb") as f:
                self._interacting_nodes = pickle.load(f)
        return self._interacting_nodes
