from pathlib import Path
from importlib.machinery import SourceFileLoader
from setuptools import find_packages, setup


version = SourceFileLoader(
    "pybiographs.version", str(Path(__file__).parent / "pybiographs" / "version.py")
).load_module()

extras = {"dl": ["torch", "torchvision"]}
setup(
    name="pybiographs",
    description="Graphs of biological data for research.",
    version=version.__version__,
    license="Apache 2.0",
    author="Synergetic AI",
    author_email="davidk@synergetic.ai",
    url="https://github.com/Synergetic-ai/Bio-knowledge-graph-python",
    download_url="https://github.com/Synergetic-ai/Bio-knowledge-graph-python",
    keywords=["covid", "data", "graphs", "research"],
    install_requires=["lz4>=3.0.0", "networkx>=2.4<3", "pandas", "requests>=2.21.0"],
    packages=find_packages(),
    extras_require=extras,
    tests_require=["pytest>=5.3.5"],
    package_data={
        "": ["LICENSE", "README.md"],
        "pybiographs": [
            "data/covid/*.pck",
            "data/covid/*.csv",
            "data/mappings/*.pck",
            "data/graphs/ontology/*.gpickle",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
    ],
)
