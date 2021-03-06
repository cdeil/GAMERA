# GAMERA

is a new open-source C++/python package which handles the spectral modelling of non-thermally emitting astrophysical sources in a simple and modular way. It allows the user to devise time-dependent models of leptonic and hadronic particle populations in a general astrophysical context (including SNRs, PWNs and AGNs) and to compute their subsequent photon emission. 

For more info and a turorial, see the [GAMERA docu!](http://joachimhahn.github.io/GAMERA/)

GAMERA is written in C++ and can be wrapped to python.

Quick Start
===========

Dependencies
------------

You need to have [GSL](http://www.gnu.org/software/gsl/) installed on your
system, as well as [SWIG](http://www.swig.org/) if you want to wrap the 
python module. If you want to locally build the docu, you also need to install
[Sphinx](http://sphinx-doc.org/), [Breathe](https://breathe.readthedocs.org/)
and [Doxygen](http://www.stack.nl/~dimitri/doxygen/).

Building
--------

Running

 - $ make all

will generate a shared object (lib/libgamera.so) as well as the python module
(lib/_gamerapy.so , lib/gamerapy.py).


