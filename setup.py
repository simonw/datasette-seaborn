from setuptools import setup
import os

VERSION = "0.2a0"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-seaborn",
    description="Statistical visualizations for Datasette using Seaborn",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-seaborn",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-seaborn/issues",
        "CI": "https://github.com/simonw/datasette-seaborn/actions",
        "Changelog": "https://github.com/simonw/datasette-seaborn/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_seaborn"],
    entry_points={"datasette": ["seaborn = datasette_seaborn"]},
    install_requires=["datasette>=0.50", "seaborn>=0.11.0"],
    extras_require={"test": ["pytest", "pytest-asyncio"]},
    tests_require=["datasette-seaborn[test]"],
)
