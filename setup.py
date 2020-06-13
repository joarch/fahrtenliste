import os

from setuptools import setup, find_packages, Command

with open(os.path.join(os.path.dirname(__file__), 'doc/README.txt')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def get_version():
    with open("VERSION.txt", 'r') as file:
        return file.readline().strip()


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass


setup(
    name="Fahrtenliste",
    version=get_version(),
    author="Jörg Ortmann",
    author_email="",
    package_dir={'': 'fahrtenliste'},
    packages=find_packages('.', exclude=["fahrtenliste", "*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    url="http://example.com",
    license="LICENSE",
    description="Fahrtenliste Webapplikation und Backend.",
    long_description=README,
    install_requires=["django",
                      "django-nested-admin",
                      "django-admin-list-filter-dropdown",
                      "python-dateutil",
                      "django-reversion",
                      "django-reversion-compare",
                      "reportlab",
                      "openpyxl<=3.0.0"
                      ],
    # extras_require={
    #    'sphinx'
    # },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    cmdclass={
        'clean': CleanCommand,
    }
)
