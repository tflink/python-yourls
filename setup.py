import sys
from setuptools import setup, Command

import yourls

install_requires = []
if (2,7) > sys.version_info:
    install_requires.append("argparse>=1.2.1")

setup(name='python-yourls',
      version=yourls.__version__,
      description='Python client for the yourls URL shortener',
      author='Tim Flink',
      author_email='tflink@fedoraproject.org',
      url='http://tflink.github.com/python-yourls/',
      packages=['yourls'],
      package_dir={'yourls':'yourls'},
      test_suite="tests",
      entry_points={
            'console_scripts':['yourls = yourls.client:main',]
          },
      install_requires=install_requires,
     )
