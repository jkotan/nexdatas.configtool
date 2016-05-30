Welcome to nxsconfigtool's documentation!
=========================================

Authors: Jan Kotanski, Eugen Wintersberger, Halil Pasic

Component Designer is a GUI configuration tool dedicated to create components 
as well as datasources which constitute the XML configuration strings of 
Nexus Data Writer (NXS). The created XML elements can be saved 
in the extended Nexus XML format in Configuration Tango Server or in disk files.


Installation from sources
=========================


Install the dependencies:

    PyQt4, PyTango (optional) 

PyTango is only needed if one wants to use Configuration Server

Download the latest NXS Configuration Tool version from

    NXS Component Designer 

and extract the sources.

One can also download the lastest version directly from the git repository by

git clone https://github.com/jkotan/nexdatas.configtool/

Next, run the installation script

$ python setup.py install


.. figure:: designer2.png
   :scale: 50 %
   :alt: component designer

   Component Designer

General overview
================

The NXS Component Designer program allows to creates components as well as 
datasources which constitute the XML configuration strings of 
Nexus Data Writer (NXS). The created XML elements can be saved 
in the extended Nexus XML format in Configuration Tango Server or in disk files.
 
Collection Dock Window contains lists of the currently open components 
and datasources. Selecting one of the components or datasources from 
the lists causes opening either Component Window or DataSource Window. 

All the most commonly used menu options are also available on Toolbar. 


Icons
=====

Icons fetched from http://findicons.com/pack/990/vistaico_toolbar.


