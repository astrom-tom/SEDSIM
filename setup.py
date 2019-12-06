from setuptools import setup  

__author__ = "Romain Thomas"
__credits__ = "Romain Thomas"
__license__ = "GNU GPL v3"
__version__ = "19.12.0"
__maintainer__ = "Romain Thomas"
__email__ = "rthomas@eso.org"
__status__ = "Development"
__website__ = "https://astrom-tom.github.io/SEDobs/build/html/index.html" 

setup(
   name = 'sedobs',
   version = __version__,
   author = __author__,
   author_email = __email__,
   packages = ['sedobs'],
   entry_points = {'gui_scripts': ['sedobs = sedobs.__main__:main',],},
   url = __website__,
   license = __license__,
   description = 'Python tool for observed galaxy SED simulation',
   python_requires = '>=3.6',
   install_requires = [
       "numpy >= 1.14.3",
       "h5py >= 2.8.0",
       "scipy >= 1.1.0",
       "tqdm >= 4.23.4",
   ],
   include_package_data=True,
)
