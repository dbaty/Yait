import os

from setuptools import find_packages
from setuptools import setup


HERE = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(HERE, 'README.rst')).read()
CHANGES = open(os.path.join(HERE, 'CHANGES.rst')).read()


REQUIRES = ('cryptacular',
            'docutils',
            'pyramid',
            'pyramid_tm',
            'sqlalchemy',
            'wtforms',
            'zope.sqlalchemy')


setup(name='Yait',
      version='0.1',
      description='Yait is an issue tracker.',
      long_description='\n\n'.join((README, CHANGES)),
      classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Pylons',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Bug Tracking'
        ),
      author='Damien Baty',
      author_email='damien.baty.remove@gmail.com',
      url='FIXME',
      keywords='web bug issue tracker pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=REQUIRES,
      test_suite='yait.tests',
      entry_points='''\
      [paste.app_factory]
      main = yait.app:make_app
      ''')
