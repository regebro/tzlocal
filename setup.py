from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='tzlocal',
      version=version,
      description="tzinfo object for the local timezone",
      long_description="""\
tzlocal contains objects for handling local timezones.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='timezone pytz dateutil',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite='tzlocal.tests',
      )
