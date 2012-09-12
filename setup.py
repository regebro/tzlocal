from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='tzlocal',
      version=version,
      description="tzinfo object for the local timezone",
      long_description=open('README.rst', 'rt').read() + '\n\n' + open('CHANGES.txt', 'rt').read(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: Unix',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='timezone pytz',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/regebro/tzlocal',
      license='CC-0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'pytz',
      ],
      test_suite='tzlocal.tests',
      )
