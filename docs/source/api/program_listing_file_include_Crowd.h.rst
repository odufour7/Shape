
.. _program_listing_file_include_Crowd.h:

Program Listing for File Crowd.h
================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_Crowd.h>` (``include/Crowd.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /* Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */
   
   #ifndef SRC_MECHANICAL_LAYER_INCLUDE_CROWD_H_
   #define SRC_MECHANICAL_LAYER_INCLUDE_CROWD_H_
   
   #include <list>
   #include <string>
   #include <vector>
   
   #include "Agent.h"
   #include "Global.h"
   
   /*  Global variable: Mechanically active agents */
   extern std::list<Agent*> mech_active_agents;
   
   /*  Functions   */
   //     Initialise scene
   int initialiseSetting(const std::string& dynamicsFile, std::vector<unsigned>& nb_shapes_allagents, std::vector<unsigned>& shapeIDagent,
                         std::vector<int>& edges, std::vector<double>& radius_allshapes, std::vector<double>& masses,
                         std::vector<double>& mois, std::vector<double2>& delta_gtos);
   int updateSetting(const std::string& dynamicsFile);
   //      Prepare mechanical layer
   bool is_mechanically_active(const Agent* agent);
   bool get_future_collision();
   void determine_agents_neighbours();
   
   //      Handle mechanical layer
   void handleMechanicalLayer(const std::string& dynamicsFile);
   //      Output
   void generateDynamicsOutputFile(const std::string& dynamicsFile);
   
   #endif   // SRC_MECHANICAL_LAYER_INCLUDE_CROWD_H_
