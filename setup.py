from setuptools import setup, find_packages


setup(
    name='namedivider-python',
    version='0.0.1',
    url='https://github.com/rskmoi/namedivider-python',
    author="rskmoi",
    author_email='rei.sakamoto.92@gmail.com',
    description='Tool for dividing Japanese name which is connected family name and given name.',
    license="MIT",
    packages=find_packages(),
    install_requires=['numpy', 'pandas', 'tqdm', 'click', 'regex'],
    tests_require=["pytest"],
    entry_points={
        'console_scripts': ['nmdiv = namedivider.cli:cmd']
    },
    package_data={'': ['namedivider/assets/*.csv']},
    include_package_data=True
)