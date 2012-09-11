from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='tzlocal',
      version=version,
      description="tzinfo object for the local timezone",
      long_description=open('README.rst', 'rt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='timezone pytz dateutil',
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
