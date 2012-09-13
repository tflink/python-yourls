from setuptools import setup, Command

import yourls

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import subprocess
        errno = subprocess.call(['py.test',  'testing'])
        raise SystemExit(errno)

setup(name='Yourls',
      version=yourls.__version__,
      description='Python client for the yourls URL shortener',
      author='Tim Flink',
      author_email='tflink@fedoraproject.org',
      url='http://tflink.github.com/python-yourls/',
      packages=['yourls'],
      package_dir={'yourls':'yourls'},
      py_modules=['yourls'],
      test_suite="tests",
      entry_points={
            'console_scripts':['yourls = yourls.client:main',]
          },
     )
