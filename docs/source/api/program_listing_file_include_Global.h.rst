
.. _program_listing_file_include_Global.h:

Program Listing for File Global.h
=================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_Global.h>` (``include/Global.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /* Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */
   
   #ifndef SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_
   #define SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_
   
   #include <sys/stat.h>
   
   #include <algorithm>
   #include <cmath>
   #include <filesystem>
   #include <fstream>
   #include <iostream>
   #include <iterator>
   #include <list>
   #include <map>
   #include <sstream>
   #include <string>
   #include <utility>
   #include <vector>
   
   //  3rd party
   #include "../3rdparty/tinyxml/tinyxml2.h"
   
   /*
       New types
                   */
   typedef std::pair<int, int> int2;
   typedef std::pair<double, double> double2;
   /*  Define operations on type double2   */
   extern double2 operator+(double2 const& a, double2 const& b);
   extern double2 operator-(double2 const& a, double2 const& b);
   extern double2 operator*(double2 const& a, double2 const& b);
   extern double2 operator*(double const coef, double2 const& R);
   extern double operator%(double2 const& a, double2 const& b);
   extern double operator!(double2 const& a);
   extern double2 operator^(double const a, double2 const& b);
   /*  Define operations on type int2  */
   extern int2 operator+(int2 const& a, int2 const& b);
   extern int2 operator-(int2 const& a, int2 const& b);
   extern int2 operator*(int2 const& a, int2 const& b);
   /*
       Global variables
                           */
   //  Geometry
   extern std::vector<std::vector<double2>> listObstacles;
   extern double Lx;
   extern double Ly;
   
   extern uint32_t nAgents;                           //  Number of agents
   extern std::map<std::string, uint32_t> agentMap;   //  Correspondence between user-given ids and internal ids
   extern std::vector<std::string> agentMapInverse;   //  Inverse version for output
   struct Agent;                                      //  Defined in Agents.h
   extern Agent** agents;                             //  The array of pointers to the agent objects
   
   extern std::map<std::pair<std::string, std::string>, uint32_t> shapeMap;   //  Correspondence between user-given
   extern std::vector<std::string> shapeMapInverse;                           //  Shape ids and internal ids. We store the
                                                                              //  couple (Agent id, shape id) in shapeMap,
                                                                              //  but the inverse map is only used for
                                                                              //  output, which is done by agent.
   
   //  Time variables
   extern double dt;        //  Time between two calls of the library
   extern double dt_mech;   //  Time step of the mechanical layer
   
   /*  Mechanical layer    */
   extern std::vector<double2> agentProperties;   //  1 / tau_mech: translational and rotational damping
   constexpr uint8_t nDefaultMaterials = 2;       //  We'll provide 2 default Materials (pedestrian and wall)
   extern uint32_t nMaterials;
   #if !defined(DOXYGEN_SHOULD_SKIP_THIS)
   enum __attribute__((__packed__))
   {
       PEDESTRIAN = 0,
       WALL = 1,
   };
   extern double** intrinsicProperties;
   constexpr int nIntrinsicProperties = 2;
   enum __attribute__((__packed__))
   {
       YOUNG_MODULUS = 0,   //  E
       SHEAR_MODULUS = 1,   //  G
   };
   extern double*** binaryProperties;
   constexpr int nBinaryProperties = 5;
   enum __attribute__((__packed__))
   {
       DAMPING_NORMAL = 0,         //  Gamma_n
       DAMPING_TANGENTIAL = 1,     //  Gamma_t
       STIFFNESS_NORMAL = 2,       //  k_n
       STIFFNESS_TANGENTIAL = 3,   //  k_t
       FRICTION_SLIDING = 4,       //  mu_dyn
   };
   #endif   // DOXYGEN_SHOULD_SKIP_THIS
   extern std::vector<int32_t> obstaclesMaterial;
   extern std::map<uint32_t, int32_t> shapesMaterial;
   
   //  Paths
   extern std::string pathStatic;
   extern std::string pathDynamic;
   
   /*
       Model parameters and user-defined constants
                                                   */
   //  Materials: default values
   constexpr double E_pedestrian = .24e+6;
   constexpr double G_pedestrian = .1e+6;
   constexpr double E_wall = .24e+6;
   constexpr double G_wall = .1e+6;
   constexpr double tau_mech_translational = 0.5;   //  0.5 corresponds to a stopping distance of 2.5 m
   constexpr double tau_mech_rotational = 0.5;
   constexpr double gamma_n = 1.3e+04;
   constexpr double gamma_t = 1.3e+04;
   constexpr double mu_dyn = 0.5;
   constexpr double gamma_n_wall = 1.3e+04;
   constexpr double gamma_t_wall = 1.3e+04;
   constexpr double mu_dyn_wall = 0.5;
   
   //  Maximum speed of an agent
   constexpr double vMaxAgent = 7.;
   
   /*
       Function declarations
                               */
   //  Utilities
   std::pair<int, double2> parse2DComponents(const char* line);
   
   //  Physics
   inline double get_interval(const double x, const double length);
   std::pair<double, double2> get_distance_to_wall_and_closest_point(double2 vertexA, double2 vertexB, const double2& C);
   double get_distance(const double2& A, const double2& B);
   
   #endif   // SRC_MECHANICAL_LAYER_INCLUDE_GLOBAL_H_
