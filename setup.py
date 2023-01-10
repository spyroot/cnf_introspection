from setuptools import setup, find_packages

setup_info = dict(name='cnf_interspect',
                  version='1.0',
                  author='Mustafa Bayramov',
                  description='Standalone or API based data interspect.',
                  author_email='spyroot@gmail.com',
                  packages=['interspect'] + ['interspect.' + pkg for pkg in find_packages('interspect')],
                  )
setup(**setup_info)