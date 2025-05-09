/* Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_CROWDMECHANICS_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_CROWDMECHANICS_H_

#include "Crowd.h"
#include "Global.h"
#include "InputStatic.h"

/*  Main    */
extern "C"
{
    //  extern C is a trick for Python ctypes to work
    int CrowdMechanics(char** files);
}

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_CROWDMECHANICS_H_
