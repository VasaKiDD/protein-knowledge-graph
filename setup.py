from setuptools import find_packages, setup
from covid_graphs.version import __version__

extras = {"dl": ["torch", "torchvision"]}
setup(
    name="covid_graphs",
    description="Covid data for research.",
    version=__version__,
    license="Apache 2.0",
    author="synergetic",
    author_email="davidk@synergetic.ai",
    url="https://github.com/VasaKiDD/covid19-knowledge-ml-python",
    download_url="https://github.com/VasaKiDD/covid19-knowledge-ml-python",
    keywords=["covid", "data", "graphs", "research"],
    install_requires=["lz4>=3.0.0", "networkx>=2.4<3", "pandas", "requests>=2.21.0"],
    packages=find_packages(),
    extras_require=extras,
    test_require=["pytest>=5.3.5"],
    package_data={
        "": ["LICENSE", "README.md"],
        "covid_graphs": [
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
