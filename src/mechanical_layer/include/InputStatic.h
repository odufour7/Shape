/* Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_INPUTSTATIC_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_INPUTSTATIC_H_

#include <map>
#include <string>
#include <vector>

#include "Global.h"

//  Read input files
int readParameters(const std::string& file);
int readMaterials(const std::string& file, std::map<std::string, int32_t>& materialMapping);
int readGeometry(const std::string& file, std::map<std::string, int32_t>& materialMapping);
int readAgents(const std::string& file, std::vector<unsigned>& nShapesPerAgent, std::vector<unsigned>& shapeIDagent,
               std::vector<int>& edges, std::vector<double>& radii, std::vector<double>& masses, std::vector<double>& mois,
               std::vector<double2>& delta_gtos, std::map<std::string, int32_t>& materialMapping);

//  Computes k_n and k_t for the given materials
double computeStiffnessNormal(const uint32_t i, const uint32_t j);
double computeStiffnessTangential(const uint32_t i, const uint32_t j);

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_INPUTSTATIC_H_
