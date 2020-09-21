from pathlib import Path

from setuptools import setup, find_packages

version = '3.0b1'

long_description = (Path('README.rst').read_text('utf-8') + '\n\n'
                    + Path('CHANGES.txt').read_text('utf-8'))


setup(name='tzlocal',
      version=version,
      description="tzinfo object for the local timezone",
      long_description=long_description,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: Unix',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='timezone pytz',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/regebro/tzlocal',
      license="MIT",
      requires_python=">=3.6",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'backports.zoneinfo; python_version < "3.9"',
      ],
      test_suite='tests',
      )
