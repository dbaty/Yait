import os

from setuptools import find_packages
from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()


REQUIRES = ('docutils',
            'pyramid',
            'pyramid_tm',
            'sqlalchemy',
            'wtforms',
            'zope.sqlalchemy')
# FIXME: repoze.who


# FIXME: to be completed
setup(name='Yait',
      version='0.1',
      description='Yait is an issue tracker.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ),
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg zope',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      test_suite="yait.tests",
      entry_points = """\
      [paste.app_factory]
      main = yait.app:make_app
      """)
