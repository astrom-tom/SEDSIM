.. _installation:

|Python36| |Licence| |numpy| |scipy| 

.. |Licence| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
      :target: http://perso.crans.org/besson/LICENSE.html

.. |Opensource| image:: https://badges.frapsoft.com/os/v1/open-source.svg?v=103
      :target: https://github.com/ellerbrock/open-source-badges/

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://www.python.org/downloads/release/python-360/

.. |numpy| image:: https://img.shields.io/badge/poweredby-numpy-orange.svg
   :target: http://www.numpy.org/

.. |scipy| image:: https://img.shields.io/badge/poweredby-scipy-orange.svg
   :target: https://www.scipy.org/


Installation
------------
------------

SEDobs is written in python 3.6 with the following library and versions:

* Numpy v1.14.3: Numerical python
* Scipy v1.1.0: Some useful function for spectral processing
* h5py  v2.8.0: hdf5 file creation and handling
* tqdm  v4.23.4: progress bar

Other libraries are used but they are all part of the standard python library. As such no extra installations are needed.

The last SEDobs version is v0.1.8 and is available in the pypi test repository. To install it:

.. code-block:: shell
     :linenos:

     pip install -i https://test.pypi.org/simple/ sedobs

Using this command will allow you not to have to install any other package. Pip will install what is missing for you.

