from setuptools import setup, find_packages

version = '2.0.0.dev0'

with open('README.rst', 'rt') as readme, open('CHANGES.txt', 'rt') as changes:
    long_description = readme.read() + '\n\n' + changes.read()


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
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='timezone pytz',
      author='Lennart Regebro',
      author_email='regebro@gmail.com',
      url='https://github.com/regebro/tzlocal',
      license="MIT",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'pytz',
      ],
      tests_require=[
          'mock',
      ],
      test_suite='tests',
      )
