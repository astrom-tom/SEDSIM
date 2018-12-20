.. _Test runs:


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


tests
-----


Some test runs have been designed for SEDOBS. They are included in the software and can be run after you install it. During the installation SEDOBS will install all the test run files in the home directory under the *.sedobs/* folder. The tests can be performed using the command:

.. code-block:: shell
     :linenos:

     sedobs --test

This command will start the tests run and will ask you to choose which test you want to perform:

.. figure:: ./pics/tests_choice.png
    :width: 750px
    :align: center

Height tests have been designed:

    * photometry [P & PG]: Only photometry is simulated. [P] uses only single distribution for the normalisation magnitude and redshift. [PG] uses the global option.
    * Single Spectroscopy [S & SG]: Only spectrosocpy is simulated in the visible. [S] uses only single distribution for the normalisation magnitude, redshift and SNR. [SG] uses the global option.
    * MultiSpectroscopy [M & MG]: Two spectra are simulated per object, one visible and one NIR. [M] uses only single distribution for the normalisation magnitude, redshift and SNR. [MG] uses the global option.
    * Full combined simulation [F & FG]: Photometry and spectroscopy are simulated. [F] uses only single distribution for the normalisation magnitude, redshift and SNR. [FG] uses the global option.











