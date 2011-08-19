from distutils.core import setup, Command

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
      version='0.1',
      description='Python client for the yourls URL shortener',
      author='Tim Flink',
      author_email='tflink@fedoraproject.org',
      url='http://localhost/something',
      packages=['yourls'],
      package_dir={'yourls':'yourls'},
      py_modules=['yourls'],
      cmdclass = {'test' : PyTest}
     )
