
.. _program_listing_file_include_MechanicalLayer.h:

Program Listing for File MechanicalLayer.h
==========================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_MechanicalLayer.h>` (``include/MechanicalLayer.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /* Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */

   #ifndef SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_
   #define SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_

   #include <array>
   #include <map>
   #include <set>
   #include <string>
   #include <tuple>
   #include <unordered_set>
   #include <utility>
   #include <vector>

   #include "Agent.h"
   #include "Global.h"

   //  Helper list to make indices explicit
   #if !defined(DOXYGEN_SHOULD_SKIP_THIS)
   enum __attribute__((__packed__)) interactionsOutput_e
   {
       SLIP = 0,
       FORCE_ORTHO = 1,
       FORCE_TAN = 2,
   };
   #endif   // DOXYGEN_SHOULD_SKIP_THIS
   struct MechanicalLayer
   {
      private:
       unsigned nb_active_agents;      //  Number of mechanically active agens
       unsigned nb_active_shapes;      //  Number of pedestrians (each pedestrian is a collection of active agents)
       std::vector<double2> vgn;       //  Velocity of the center of mass (CM) of each pedestrian at t
       std::vector<double2> vgnp1;     //  Velocity of the CM of each pedestrian at t+dt
       std::vector<double2> rgcomp;    //  Initial positions of all the components of the pedestrians
       std::vector<double2> rgn;       //  Positions of the CM of each pedestrian at t
       std::vector<double2> rgnp1;     //  Positions of the CM of each pedestrian at t+dt
       std::vector<double2> delta;     //  Difference between position of the CM of each component and
                                       //  the CM of their associated pedestrian
       std::vector<double> thetn;      //  Orientation wrt x-axis at t
       std::vector<double> thetnp1;    //  Orientation wrt x-axis at t+dt
       std::vector<double> wn;         //  Angular velocity at t
       std::vector<double> wnp1;       //  Angular velocity at t+dt
       std::vector<double> wdesired;   //  Desired orientation wrt x-axis
                                       //  Forces have the dimension of an acceleration
       std::vector<double2> Fp;        //  Propelling force v_des/tau_mech
       std::vector<double2> Forthon;   //  Orthogonal force (hertz) wrt contact surface at time t
       std::vector<double2> Ftn;       //  Tangential force wrt contact surface at time t
       std::vector<double> taun;       //  Torque at time t (moment projected on z-axis) expressed at the CM
       std::vector<std::list<int>> neighbours;
       std::vector<unsigned> active_shapeIDagent;         //  Pedestrian id of each shape
       std::vector<unsigned> active_shapeIDshape_crowd;   //  Shape id of each pedestrian
       std::vector<double> radius;                        //  Radius off all shapes of actives agents
       std::vector<unsigned> size_agents;
       std::map<unsigned, unsigned> agentIds;
       std::vector<unsigned> agentActiveIds;
       std::vector<std::vector<unsigned>> neighbours_shape;
       std::vector<unsigned> agentIDshape;
       std::vector<double> masses;
       std::vector<double> mois;
       std::vector<double2> damping;

       //  Tangential relative displacement when in contact
       std::map<std::pair<unsigned, unsigned>, double2> slip;
       std::map<std::tuple<unsigned, int, int>, double2> slip_wall;

       //  For output purposes: the following variables will contain:
       //    - a copy of slip
       //    - fortho from shape to shape
       //    - ft from shape to shape
       std::map<std::pair<unsigned, unsigned>, std::array<double2, 3>> interactionsOutput;
       std::map<std::tuple<unsigned, int, int>, std::array<double2, 3>> interactionsOutputWall;

       std::tuple<double2, double2, double> get_interactions(unsigned cpt_shape, bool AtTimen);
       void loop();
       //  AgentInteractions is an input and output file (ie "dynamic") of this process
       int readInteractionsInputFile(const std::string& interactionsFile);
       std::pair<bool, bool> existsContacts();   //  Do contacts exist?
       void generateInteractionsOutputFile(const std::string& interactionsFile, const std::pair<bool, bool>& exists);

      public:
       explicit MechanicalLayer(std::list<Agent*>& mech_active_agents);
       ~MechanicalLayer();
   };

   #endif   // SRC_MECHANICAL_LAYER_INCLUDE_MECHANICALLAYER_H_"
