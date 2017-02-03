# -*- coding: utf-8 -*-
"""
SETUP de esiosdata: Web Scraper para datos de demanda, producción y coste de la energía eléctrica en España.
"""
from setuptools import setup, find_packages
from esiosdata import __version__ as version


packages = find_packages(exclude=['docs', '*tests*', 'notebooks', 'htmlcov'])

setup(
    name='esiosdata',
    version=version,
    description='Web Scraper para datos de demanda, producción y coste de la energía eléctrica en España, '
                'y simulador de facturación eléctrica según el PVPC..',
    # TODO Long description para PYPI
    keywords='web scraper, energy, esios, ree, pvpc, electricidad',
    author='Eugenio Panadero',
    author_email='azogue.lab@gmail.com',
    url='https://github.com/azogue/esiosdata',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Spanish',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ],
    packages=packages,
    package_data={
        'esiosdata': ['templates/*'],
    },
    install_requires=['termcolor', 'pandas', 'pytz', 'numpy', 'matplotlib', 'seaborn', 'dataweb', 'jinja2'],
    entry_points={
        'console_scripts': ['esiosdata = esiosdata.__main__:main_cli']
    },
    tests_require=['pytest>=3.0.0'],
)

