from glob import glob
from os.path import basename, splitext
from setuptools import setup, find_packages

setup(
    name='py-enigma',
    version='0.1.0',
    description='Enigma machine simulator',
    author='Dave MacGugan',
    author_email='dave@macgugan.net',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    python_requires='>=3.8',
    install_requires=[
        "windows-curses; platform_system=='Windows'",
    ],
    package_data={"enigma": ["data/*.json"]},
    entry_points={
        "console_scripts": [
            "enigma=enigma.cli:main",
            "enigma-utils=enigma.utils_cli:main",
        ],
    },
)
