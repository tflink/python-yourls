from distutils.core import setup

setup(name='Yourls',
      version='0.1',
      description='Python client for the yourls URL shortener',
      author='Tim Flink',
      author_email='tflink@fedoraproject.org',
      url='http://localhost/something',
      packages=['yourls'],
      package_dir={'yourls':'yourls'},
      py_modules=['yourls']
     )
