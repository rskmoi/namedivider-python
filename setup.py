from setuptools import setup, find_packages
from namedivider import __version__

setup(
    name='namedivider-python',
    version=__version__,
    url='https://github.com/rskmoi/namedivider-python',
    author="rskmoi",
    author_email='rei.sakamoto.92@gmail.com',
    description='A tool for dividing the Japanese full name into a family name and a given name.',
    license="MIT",
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'tqdm', 'click', 'regex'],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': ['nmdiv = namedivider.cli:cmd']
    },
    package_data={'': ['namedivider/assets/*.csv']},
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ]
)
