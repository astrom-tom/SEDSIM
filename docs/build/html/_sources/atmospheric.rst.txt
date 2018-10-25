.. _atmospherique:


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


Atmospheric effects
-------------------
-------------------

In the spirit of making SEDOBS as complete as possible two atmospheric effects have been implemented: the atmospheric extinction and sky emission. Both effects have been made based on model computed for the Paranal Observatory. These modelisations are public and maintained by the European Southern Observatory (ESO). We use the v2.0.4 Cerro Paranal Advanced Sky Model (Available `here <http://www.eso.org/observing/etc/bin/gen/form?INS.MODE=swspectr+INS.NAME=SKYCALC>`_).
We detail how these effects have been implemented in SEDOBS in the following sections.

Telluric Absorption
^^^^^^^^^^^^^^^^^^^
The earth atmosphere has a heavy impact on the flux reaching our ground-based observatory. It acts as a screen that is going to attenuate the flux of the distant object we are observing. This attenuation heavily depends on the wavelength at which it is considered as well as on the airmass (AM) at which the observation is taken (see figure below). 

.. figure:: ./pics/TellTrspectra.png
    :width: 750px
    :align: center
    :alt: Example of atmospheric transmission model above the Cerro Paranal at different airmasses.

SEDOBS allows you to add atmospheric attenuation in the simulated data if you wish to do so. As the data configuration can include both space and ground-based data the definition of observation place (ground or space) must be precised for each spectrum and/or band that is simulated (see :doc:`configuration` for more details about how you have to tell SEDOBS in practice). SEDOBS as implemented three groups of AIRMASS ranges that can be used: low, intermediate and high. Using the **low** range will apply randomly the attenuation considering AM between 1 and 1.15 (corresponding to altitudes between 90 degrees and 60.4 degrees). Using the **intermediate** range of airmass will assign randomly an AM between 1.15 and 1.4 (equivalent to altitudes of 60.4 degrees and 45.5 degrees). Finally, the **high** airmass range will be using airmasses above 1.4 up to 2.95 (altitude of 45.4 and 19.8 degrees, 19.5 degree being the limit of the model and below the pointing limit of the Unit telescope of the VLT). SEDOBS contain 10 curves of attenuation between AM=1 and AM=2.95. Values of AM where no curves was created will be linearly interpolated. Therefore observations can have any value in a given range with a precision on the AM of 0.05.


Sky Emission
^^^^^^^^^^^^

You also have the possibility to include sky lines in the mock observations. The sky model of Cerro Paranal produces, alongside the telluric absorption, the sky emission model. As for the atmospheric attenuation, this emission will depend strongly on the wavelength and on the AM at which you simulate the observations. For this reason the sky emission is implemented in the same way as the atmospheric attenuation: in three AM ranges (see above). The ESO modelisation provides the sky radiance in :math:`[ph/s/m^2/\mu m/ arcsec^2]` and can be seen in the figure below: 

.. figure:: ./pics/skyspectra.png
    :width: 750px
    :align: center
    :alt: ses.

We convert this to :math:`[erg/s/cm^2/Ang/arcsec^2]` using:

.. figure:: ./pics/convertsky.png
    :width: 750px
    :align: center
    :alt: ses.

As we need to convert this to a flux density :math:`[erg/s/cm^2/Ang]` we need to consider a angular size in the sky for our galaxy. The default value is set to :math:`1''`. This value can be easily changed in the configuration file (see :doc:`configuration`).
When simulating photometry SEDOBS adds up the skyline spectrum to the synthetic spectrum before computing the magnitudes. In the case of spectroscopy, SEDOBS adapts the resolution of the skyline spectrum to the resolution of the simulated observation and then adds it up to the synthetic template as well. The noise estimation is then computed on the addition of the galaxy synthetic template and the skyline template.

