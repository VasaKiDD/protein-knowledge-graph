import pandas
import pytest

from pybiographs.covid_data import CovidData


@pytest.fixture()
def covid_data():
    return CovidData()


class TestCovidData:
    def test_df(self, covid_data):
        assert covid_data._df is None
        assert isinstance(covid_data.df, pandas.DataFrame)

    def test_dict(self, covid_data):
        assert covid_data._dict is None
        assert isinstance(covid_data.dict, dict)

    def test_interacting_nodes(self, covid_data):
        assert covid_data._interacting_nodes is None
        nodes = covid_data.interacting_nodes
        assert isinstance(nodes, dict)
        for n in nodes.keys():
            assert isinstance(n, str)

    def test_names(self, covid_data):
        for name in covid_data.names:
            assert getattr(covid_data, name) is not None

    def test_dict_wrapper(self, covid_data):
        for k in covid_data.keys():
            data = covid_data[k]
            assert data is not None
