import math
import os
import tempfile
from typing import Tuple

import lz4.frame
import requests
from tqdm.auto import tqdm

from pybiographs.resources import get_interactions_path, interaction_file_names, interaction_files


def download_interactions_graph(directed: bool, output=None) -> None:
    """
    Download and decompress the data corresponding to the target interaction graph.

    Args:
        directed: If ``True`` the data corresponding to the directed graph of
                  interactions will be downloaded. If ``False`` the data corresponding
                  to the undirected graph of interactions will be downloaded.
        output: Output path where the downloaded data will be store. Defaults to
                the package_data folder

    Returns:
        None

    """
    if output is None:
        output = (
            _InteractionsDownloader.DEFAULT_DIRECTED_FILEPATH
            if directed
            else _InteractionsDownloader.DEFAULT_UNDIRECTED_FILEPATH
        )
    if directed:
        _InteractionsDownloader.download_directed_interactions(output=output)
    else:
        _InteractionsDownloader.download_undirected_interactions(output=output)


class _InteractionsDownloader:

    DIRECTED_URL = (
        "https://github.com/Synergetic-ai/Bio-knowledge-graph-python/raw/"
        "master/data/graphs/interactions/directed/"
        "pp_interactions_directed.gpickle.lz4"
    )
    UNDIRECTED_URLS = (
        "https://github.com/Synergetic-ai/Bio-knowledge-graph-python/raw/master/data/graphs/"
        "interactions/undirected/undirectedaa.part",
        "https://github.com/Synergetic-ai/Bio-knowledge-graph-python/raw/master/data/graphs/"
        "interactions/undirected/undirectedab.part",
    )
    DEFAULT_INTERACTIONS_PATH = get_interactions_path()
    DEFAULT_DIRECTED_NAME = interaction_file_names.directed
    DEFAULT_UNDIRECTED_NAME = interaction_file_names.undirected
    DEFAULT_DIRECTED_FILEPATH = interaction_files.directed
    DEFAULT_UNDIRECTED_FILEPATH = interaction_files.undirected

    @classmethod
    def download_directed_interactions(
        cls, download_url: str = DIRECTED_URL, output: str = DEFAULT_DIRECTED_FILEPATH
    ):
        headers = {"Accept": "application/vnd.github.v3.raw"}
        with requests.get(download_url, headers=headers, stream=True) as req:
            # Total size in bytes.
            total_size = int(req.headers.get("content-length", 0))
            one_kb = 1000
            req.raise_for_status()
            temp_dir = tempfile.mkdtemp(prefix="directed")
            temp_file = os.path.join(temp_dir, "directed.lz4")
            with open(temp_file, "wb") as f:
                for chunk in tqdm(
                    req.iter_content(one_kb),
                    total=math.ceil(total_size // one_kb),
                    unit="KB",
                    mininterval=0.25,
                    unit_scale=True,
                    desc="Downloading graph data",
                ):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            os.listdir(cls.DEFAULT_INTERACTIONS_PATH)
            cls._decompress_and_save_file(temp_file, output)

    @classmethod
    def download_undirected_interactions(
        cls, download_urls: Tuple[str] = UNDIRECTED_URLS, output: str = DEFAULT_UNDIRECTED_FILEPATH
    ):
        def iterate_chunks(reqs):
            for req in reqs:
                for chunk in req.iter_content(one_kb):
                    yield chunk

        headers = {"Accept": "application/vnd.github.v3.raw"}
        with requests.Session() as s:
            reqs = [s.get(url, headers=headers, stream=True) for url in download_urls]
            total_size = sum([int(req.headers.get("content-length", 0)) for req in reqs])
            one_kb = 1000
            for req in reqs:
                req.raise_for_status()
            temp_dir = tempfile.mkdtemp(prefix="undirected")
            temp_file = os.path.join(temp_dir, "undirected.lz4")
            with open(temp_file, "wb") as f:
                for chunk in tqdm(
                    iterate_chunks(reqs),
                    total=math.ceil(total_size // one_kb),
                    unit="KB",
                    mininterval=0.25,
                    unit_scale=True,
                    desc="Downloading graph data",
                ):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            os.listdir(cls.DEFAULT_INTERACTIONS_PATH)
            cls._decompress_and_save_file(temp_file, output)

    @staticmethod
    def _decompress_and_save_file(input_path: str, output_path: str) -> None:
        with open(input_path, "rb") as f:
            data = lz4.frame.decompress(f.read())
        with open(output_path, "wb") as f:
            f.write(data)
