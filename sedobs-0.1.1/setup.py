from setuptools import setup  
import sedobs.__info__ as sed

setup(
   name = 'sedobs',
   version = sed.__version__,
   author = sed.__author__,
   author_email = sed.__email__,
   packages = ['sedobs'],
   entry_points = {'gui_scripts': ['sedobs = sedobs.__main__:main',],},
   url = sed.__website__,
   license = sed.__license__,
   description = 'Python tool for observed galaxy SED simulation',
   python_requires = '>=3.6',
   install_requires = [
       "numpy >= 1.14.2",
       "h5py >= 2.8.0",
       "scipy >= 1.0.1",
       "tqdm >= 4.23.4"
   ],
   include_package_data=True,
)
