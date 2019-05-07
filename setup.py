# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='convirt',
    version='2.0',
    description='',
    author='',
    author_email='',
    #url='',
    install_requires=[
        "TurboGears2 == 2.0.3",
        #"Catwalk >= 2.0.2",
        "Babel >=0.9.4",
        #can be removed iif use_toscawidgets = False
        #"toscawidgets >= 0.9.7.1",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        
        "repoze.what-quickstart >= 1.0",
        # Jd
        "paramiko >= 1.7.3",
        #"tgrum",
        "simplejson >= 2.0.9",
        "hashlib",
	"Beaker >= 1.4",
        "SQLAlchemy == 0.5.6",
        "MySQL-python >= 1.2.2"
                ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'convirt': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'convirt': [
        ('**.py', 'python', None),
        #('templates/**.mako', 'mako', None),
        #('templates/**.html', 'genshi', None),
        ('public/javascript/*.js', 'javascript', None),
        ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = convirt.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
