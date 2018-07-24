from setuptools import setup  # Always prefer setuptools over distutils
import photon.__info__ as phot
print(phot.__dict__.keys())

setup(
   name = 'sedsim',
   version = phot.__version__,
   author = phot.__author__,
   author_email = phot.__email__,
   packages = ['sedsim'],
   entry_points = {'gui_scripts': ['sedsim = sedsim.__main__:main',],},
   url = phot.__website__,
   license = phot.__license__,
   description = 'Python tool for galaxy SED simulation',
   python_requires = '>=3.6',
   install_requires = [
   ],
   include_package_data=True,
)
