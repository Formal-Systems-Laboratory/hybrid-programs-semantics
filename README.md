The Semantics of Hybrid Programs in K
=====================================

Hybrid Programs (HP) is a modeling formalism that is primarily used
to express semantics of Hybrid System in [Differential Dynamic
Logic](http://symbolaris.com/logic/dL.html)(dL). Loosely put,
dL is a variant of First Order Dynamic
Logic (FO-DL) with Reals as the domain of computation, and Hybrid
Programs extend FO-DL programs with constructs for continuous
evolution. This repository contains the semantics of HP
in K.

Requirements
------------

Mathematica 12 is required operations over Reals
and Quantifier Elimination in constraint synthesis.

Building & Running
------------------

 * `./build` will build and run all the execution tests

 * `./khp run <FILE>` to run a particular HP file
