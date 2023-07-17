from setuptools import setup, find_packages
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('kiwoom/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(
    name            = 'kiwoom',
    version         = main_ns['__version__'],
    description     = 'To use Kiwoom API easily and conveniently',
    url             = 'https://github.com/warvirus/ats',
    author          = 'Jason Lee',
    author_email    = 'warvirus10041@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires= ['requests', 'pandas', 'datetime', 'numpy', 'xlrd', 'deprecated'],
    license         = 'MIT',
    packages        = find_packages(include=['kiwoom', 'kiwoom.*', 'kiwoom.kiwoom.*', 'kiwoom.ui.*', 'kiwoom.utils.*']),
    python_requires = '>=3.8',
    zip_safe        = False
)