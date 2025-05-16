
.. _program_listing_file_src_MechanicalLayer.cpp:

Program Listing for File MechanicalLayer.cpp
============================================

|exhale_lsh| :ref:`Return to documentation for file <file_src_MechanicalLayer.cpp>` (``src/MechanicalLayer.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
       Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
       This file contains the actual mechanical layer, which will take mechanically active agents and handle possible collisions.
    */
   
   #include "MechanicalLayer.h"
   
   #include <iostream>
   #include <list>
   #include <set>
   #include <string>
   #include <tuple>
   #include <utility>
   #include <vector>
   using std::list, std::map, std::set, std::vector, std::string, std::tuple, std::pair, std::cout, std::cerr, std::endl, std::ofstream,
       std::fmin;
   
   MechanicalLayer::MechanicalLayer(list<Agent*>& mech_active_agents)
       : nb_active_agents(mech_active_agents.size()),
         nb_active_shapes(0),
         vgn(nb_active_agents),
         vgnp1(nb_active_agents),
         rgn(nb_active_agents),
         rgnp1(nb_active_agents),
         delta(0),
         thetn(nb_active_agents),
         thetnp1(nb_active_agents),
         wn(nb_active_agents),
         wnp1(nb_active_agents),
         wdesired(nb_active_agents),
         Fp(nb_active_agents),
         Forthon(nb_active_agents),
         Ftn(nb_active_agents),
         taun(nb_active_agents),
         neighbours(nb_active_agents),
         active_shapeIDagent(0),
         active_shapeIDshape_crowd(0),
         radius(0),
         size_agents(nb_active_agents),
         neighbours_shape(nb_active_agents),
         agentIDshape(nb_active_agents + 1, 0),
         masses(nb_active_agents),
         mois(nb_active_agents),
         damping(nb_active_agents)
   {
       /*  Preliminary definitions and initialisation  */
       //  Sort mechanically active agents
       mech_active_agents.sort([](auto const& a, auto const& b) { return (a->_id) < (b->_id); });
       unsigned cpt_agent = 0;
       for (Agent* agent : mech_active_agents)
       {
           for (unsigned cpt_shape(0); cpt_shape < agent->_nb_shapes; cpt_shape++)
           {
               active_shapeIDagent.push_back(cpt_agent);
               active_shapeIDshape_crowd.push_back(agent->_ids_shapes[cpt_shape]);
           }
           agentIds[agent->_id] = cpt_agent;
           agentActiveIds.push_back(agent->_id);
           vector<double2> delta_gtos_agent = agent->get_delta_gtos();
           delta.insert(delta.end(), (delta_gtos_agent).begin(), (delta_gtos_agent).end());
           radius.insert(radius.end(), (agent->_radius_shapes).begin(), (agent->_radius_shapes).end());
           size_agents[cpt_agent] = agent->_nb_shapes;
           nb_active_shapes += agent->_nb_shapes;
           rgn[cpt_agent] = double2(agent->_x, agent->_y);
           thetn[cpt_agent] = agent->_theta;
           vgn[cpt_agent] = double2(agent->_vx, agent->_vy);
           wn[cpt_agent] = agent->_w;
           masses[cpt_agent] = agent->_mass;
           mois[cpt_agent] = agent->_moi;
           damping[cpt_agent] = agentProperties[agent->_id];
   
           rgnp1[cpt_agent] = double2(agent->_x, agent->_y);
           thetnp1[cpt_agent] = agent->_theta;
           vgnp1[cpt_agent] = double2(agent->_vx, agent->_vy);
           wnp1[cpt_agent] = agent->_w;
           const double inverseTauMechTranslation = agentProperties[agent->_id].first;
           //  The "F" here have the dimension of an acceleration
           Fp[cpt_agent] = inverseTauMechTranslation * agent->_v_des;   //  We recompute Fp from v_des...
           Forthon[cpt_agent] = double2(0., 0.);
           Ftn[cpt_agent] = double2(0., 0.);
           taun[cpt_agent] = 0.;
           wdesired[cpt_agent] = agent->_w_des;
   
           cpt_agent++;
       }
   
       //  Get the correspondence between agent and shapes  (ie the edges)
       unsigned length(0);
       for (size_t a = 0; a < nb_active_agents; ++a)
       {
           length += size_agents[a];
           agentIDshape[a + 1] = length;
       }
   
       //  Get neighbouring shapes id of each agent
       cpt_agent = 0;
       for (const Agent* agent : mech_active_agents)
       {
           unsigned cpt_agent2 = 0;
           for (const Agent* agent2 : mech_active_agents)
           {
               if (cpt_agent2 > cpt_agent)
               {
                   //  Include as neighbour if within 5*(r1+r2) where r1 and r2 are the size of the body (the radius of the smallest
                   //  circle containing all the shapes)
                   if (const double distance = !(rgn[cpt_agent] - rgn[cpt_agent2]); distance < 5.0 * (agent->_radius + agent2->_radius))
                   {
                       for (unsigned cpt_shape(agentIDshape[cpt_agent2]); cpt_shape < agentIDshape[cpt_agent2] + size_agents[cpt_agent2];
                            ++cpt_shape)
                           neighbours_shape[cpt_agent].push_back(cpt_shape);
                       for (unsigned cpt_shape(agentIDshape[cpt_agent]); cpt_shape < agentIDshape[cpt_agent] + size_agents[cpt_agent];
                            ++cpt_shape)
                           neighbours_shape[cpt_agent2].push_back(cpt_shape);
                   }
               }
               cpt_agent2++;
           }
           cpt_agent++;
       }
   
       /*  Check if an Interactions File already exists    */
       const string interactionsFile = pathDynamic + "AgentInteractions.xml";
       struct stat buffer{};
       if (stat(interactionsFile.c_str(), &buffer) != -1)
           readInteractionsInputFile(interactionsFile);
   
       /*  MECHANICAL Loop */
       for (unsigned t = 0; t < static_cast<unsigned>(dt / dt_mech); t++)
       {
           loop();
       }
   
       /*  Update the positions and velocities of mechanically active agents   */
       cpt_agent = 0;
       for (Agent* agent : mech_active_agents)
       {
           agent->_x = rgn[cpt_agent].first;
           agent->_y = rgn[cpt_agent].second;
           agent->_vx = vgn[cpt_agent].first;
           agent->_vy = vgn[cpt_agent].second;
           agent->_theta = thetn[cpt_agent];
           agent->_w = wn[cpt_agent];
           cpt_agent++;
       }
   
       /*  Output the interactions file */
       generateInteractionsOutputFile(interactionsFile, existsContacts());
   }
   
   MechanicalLayer::~MechanicalLayer()   // destructor transfers computed data to the agents
       = default;
   
   int MechanicalLayer::readInteractionsInputFile(const std::string& interactionsFile)
   {
       tinyxml2::XMLDocument document;
       document.LoadFile(interactionsFile.data());
       if (document.ErrorID() != 0)
       {
           cerr << "Error: Could not load or parse XML file " << interactionsFile << endl;
           return EXIT_FAILURE;
       }
   
       //  Read the Interactions block
       const tinyxml2::XMLElement* interactionsElement = document.FirstChildElement("Interactions");
       if (!interactionsElement)
       {
           cerr << "Error: interactions must be embedded in \"Interactions\" tag!" << endl;
           return EXIT_FAILURE;
       }
   
       const tinyxml2::XMLElement* agent1Element = interactionsElement->FirstChildElement("Agent");
       if (!agent1Element)
       {
           cerr << "Error: no Agent tag present in " << interactionsFile << endl;
           return EXIT_FAILURE;
       }
       while (agent1Element)
       {
           const char* agent1ExternId = nullptr;
           if (agent1Element->QueryStringAttribute("Id", &agent1ExternId) != tinyxml2::XML_SUCCESS)
           {
               cerr << "Error: Agents must have an Id in file " << interactionsFile << endl;
               return EXIT_FAILURE;
           }
           //  Interactions with other agents
           const tinyxml2::XMLElement* agent2Element = interactionsElement->FirstChildElement("Agent");
           if (!agent2Element)
           {
               cerr << "Error: no Agent neighbour present in " << interactionsFile << endl;
               return EXIT_FAILURE;
           }
           while (agent2Element)
           {
               const char* agent2ExternId = nullptr;
               if (agent2Element->QueryStringAttribute("Id", &agent2ExternId) != tinyxml2::XML_SUCCESS)
               {
                   cerr << "Error: Agents must have an Id in file " << interactionsFile << endl;
                   return EXIT_FAILURE;
               }
               //  Read interactions
               const tinyxml2::XMLElement* interactionElement = agent2Element->FirstChildElement("Interaction");
               while (interactionElement)
               {
                   int32_t shapeParent;
                   int32_t shapeChild;
                   if (interactionElement->QueryIntAttribute("ParentShape", &shapeParent) != tinyxml2::XML_SUCCESS)
                   {
                       cerr << "Error: no shape identifier in interaction between agents in " << interactionsFile << endl;
                       return EXIT_FAILURE;
                   }
                   if (interactionElement->QueryIntAttribute("ChildShape", &shapeChild) != tinyxml2::XML_SUCCESS)
                   {
                       cerr << "Error: no shape identifier in interaction between agents in " << interactionsFile << endl;
                       return EXIT_FAILURE;
                   }
                   const char* buffer = nullptr;
                   interactionElement->QueryStringAttribute("TangentialRelativeDisplacement", &buffer);
                   auto [rcSlip, inputSlip] = parse2DComponents(buffer);
                   uint32_t cpt_shape          = agentIDshape[agentMap[agent1ExternId]] + shapeParent;
                   uint32_t cpt_shape_neigh    = agentIDshape[agentMap[agent2ExternId]] + shapeChild;
   
                   slip[{cpt_shape, cpt_shape_neigh}] = inputSlip;
                   slip[{cpt_shape_neigh, cpt_shape}] = -1 * inputSlip;
               }
   
               agent2Element = agent2Element->NextSiblingElement("Agent");
           }
           //  Interactions with walls
           const tinyxml2::XMLElement* wallElement = agent1Element->FirstChildElement("Wall");
           while (wallElement)
           {
               int32_t shape;
               wallElement->QueryIntAttribute("ShapeId", &shape);
               int obstacleId, wallId;
               wallElement->QueryIntAttribute("ObstacleId", &obstacleId);
               wallElement->QueryIntAttribute("WallId", &wallId);
               const char* buffer = nullptr;
               wallElement->QueryStringAttribute("TangentialRelativeDisplacement", &buffer);
               auto [rcSlipWall, inputSlipWall] = parse2DComponents(buffer);
               uint32_t cpt_shape = agentIDshape[agentMap[agent1ExternId]] + shape;
               slip_wall[{cpt_shape, obstacleId, wallId}] = inputSlipWall;
   
               wallElement = wallElement->NextSiblingElement("Wall");
           }
           agent1Element = agent1Element->NextSiblingElement("Agent");
       }
   
       return EXIT_SUCCESS;
   }
   
   tuple<double2, double2, double> MechanicalLayer::get_interactions(unsigned cpt_shape, bool AtTimen)
   {
       unsigned cpt_agent = active_shapeIDagent[cpt_shape];
       double UnmZetadt = 1.0 - dt_mech * damping[cpt_agent].first;
       double2 delta_GtoS = AtTimen ? delta[cpt_shape] : delta[cpt_shape] + ((thetnp1[cpt_agent] - thetn[cpt_agent]) ^ delta[cpt_shape]);
       double2 posagent = AtTimen ? rgn[cpt_agent] : rgnp1[cpt_agent];   //  Center of mass of the agent
       double2 posshape = posagent + delta_GtoS;                         //  Center of mass of the shape
       double angvel =   //  Angular velocity of the shape at time n and trial angular velocity for the time n+1
           AtTimen ? wn[cpt_agent] : wn[cpt_agent] + dt_mech * taun[cpt_agent];
       double2 velagent =   //  Velocity of the shape (v_shape(t+dt) = v_CM(t+dt))
           AtTimen ? vgn[cpt_agent] : UnmZetadt * vgn[cpt_agent] + dt_mech * (Fp[cpt_agent] + Forthon[cpt_agent] + Ftn[cpt_agent]);
       double2 velshape = velagent + (angvel ^ delta_GtoS);
   
       double torq = 0.;
       double2 fortho(0., 0.);
       double2 ft(0., 0.);
   
       /*  Interactions between agents */
       for (unsigned cpt_shape_neigh : neighbours_shape[cpt_agent])
       {
           unsigned cpt_neigh = active_shapeIDagent[cpt_shape_neigh];
           double2 delta_GtoS_neigh = AtTimen
                                          ? delta[cpt_shape_neigh]
                                          : delta[cpt_shape_neigh] + ((thetnp1[cpt_neigh] - thetn[cpt_neigh]) ^ delta[cpt_shape_neigh]);
           double2 posagent_neigh = AtTimen ? rgn[cpt_neigh] : rgnp1[cpt_neigh];
           double2 posshape_neigh = posagent_neigh + delta_GtoS_neigh;
           double angvel_neigh = AtTimen ? wn[cpt_neigh] : wn[cpt_neigh] + dt_mech * taun[cpt_neigh];
           double2 velagent_neigh =   //  Velocity of the CM of the neighbouring pedestrian neighbour
               AtTimen ? vgn[cpt_neigh] : UnmZetadt * vgn[cpt_neigh] + dt_mech * (Fp[cpt_neigh] + Forthon[cpt_neigh] + Ftn[cpt_neigh]);
           double2 velshape_neigh = velagent_neigh + (angvel_neigh ^ delta_GtoS_neigh);
   
           double2 r_ij = posshape - posshape_neigh;
           double distance(!r_ij);
           double2 n_ij;
           if (distance == 0.)
               n_ij = double2(0., 0.);
           else
               n_ij = (1. / distance) * r_ij;
           double h(radius[cpt_shape] + radius[cpt_shape_neigh] - distance);   //  Indentation
           double2 dcGshape = -(radius[cpt_shape] - h / 2.) * n_ij;            //  From the center of mass G of the shape
                                                                               //  towards c (the contact point)
           double2 dcGshapeneigh = +(radius[cpt_shape_neigh] - h / 2.) * n_ij;
           double2 dcG = delta[cpt_shape] + dcGshape;   //  Vector distance from CM of the agent to
                                                        //  c = vector distance from CM agent to CM shape +
                                                        //      distance from CM shape to c
           //  If the two shapes are in contact:
           if (h > 0.)
           {
               double2 v_ci = velshape + (angvel ^ dcGshape);                    //  Velocity of i at the contact point
               double2 v_cj = velshape_neigh + (angvel_neigh ^ dcGshapeneigh);   //  Velocity of j at the contact point
               double2 vij = v_ci - v_cj;
               double2 vortho_ij = (vij % n_ij) * n_ij;
               double2 vt_ij = vij - vortho_ij;
               double norm_vt_ij = !vt_ij;
   
               //  If the map does not contain this pair ie the slip is not initialized, we initialize it
               //  Otherwise: we increment it
               if (!slip.contains({cpt_shape, cpt_shape_neigh}))
                   slip[{cpt_shape, cpt_shape_neigh}] = double2(0., 0.);
               else
                   slip[{cpt_shape, cpt_shape_neigh}] = slip[{cpt_shape, cpt_shape_neigh}] + dt_mech * vt_ij;
               //  For the output Interactions file:
               //  We will only put the N(N-1)/2 pairs, ie cpt_shape_neigh>cpt_shape
               if (!interactionsOutput.contains({cpt_shape_neigh, cpt_shape}))
                   interactionsOutput[{cpt_shape, cpt_shape_neigh}][SLIP] = slip[{cpt_shape, cpt_shape_neigh}];
   
               double2 delta_tij = slip[{cpt_shape, cpt_shape_neigh}];   //  Vector of tangential displacement
               double norm_delta_tij = !delta_tij;
   
               double2 t_vij;
               if (norm_vt_ij > 0)
                   t_vij = (1. / norm_vt_ij) * vt_ij;
               else if (norm_delta_tij > 0)
                   t_vij = (1. / norm_delta_tij) * delta_tij;
               else
                   t_vij = double2(0., 0.);
   
               uint32_t shapeMaterialId = shapesMaterial[active_shapeIDshape_crowd[cpt_shape]];
               uint32_t shapeNeighbourMaterialId = shapesMaterial[active_shapeIDshape_crowd[cpt_shape_neigh]];
               /*  Normal interactions */
               double k_n = binaryProperties[STIFFNESS_NORMAL][shapeMaterialId][shapeNeighbourMaterialId];
               double Gamma_n = binaryProperties[DAMPING_NORMAL][shapeMaterialId][shapeNeighbourMaterialId];
               double2 fnij_elastic = k_n * h * n_ij;
               double2 fnij_viscous = -Gamma_n * vortho_ij;
               double2 fnij = fnij_elastic + fnij_viscous;
               fortho = fortho + fnij;
               if (!interactionsOutput.contains({cpt_shape_neigh, cpt_shape}))
                   interactionsOutput[{cpt_shape, cpt_shape_neigh}][FORCE_ORTHO] = fnij;
   
               /*  Tangential interactions */
               double k_t = binaryProperties[STIFFNESS_TANGENTIAL][shapeMaterialId][shapeNeighbourMaterialId];
               double Gamma_t = binaryProperties[DAMPING_TANGENTIAL][shapeMaterialId][shapeNeighbourMaterialId];
               double2 ftij_spring = -k_t * norm_delta_tij * t_vij;
               double2 ftij_viscous = -Gamma_t * vt_ij;
               double2 ftij_static = ftij_spring + ftij_viscous;
               double mu_dyn = binaryProperties[FRICTION_SLIDING][shapeMaterialId][shapeNeighbourMaterialId];
               double2 ftij_dynamic = -mu_dyn * !fnij * t_vij;
               double2 ftij = -1. * fmin(!ftij_static, !ftij_dynamic) * t_vij;
               ft = ft + ftij;
               if (!interactionsOutput.contains({cpt_shape_neigh, cpt_shape}))
                   interactionsOutput[{cpt_shape, cpt_shape_neigh}][FORCE_TAN] = ftij;
   
               /*  Torque  */
               double torqnij = (1. ^ dcG) % fnij;
               double torqtij = (1. ^ dcG) % ftij;
               double torqij = torqnij + torqtij;
               torq = torq + torqij;
           }
       }
   
       /*  Interactions with walls */
       int iobs = 0;
       for (vector<double2> const& wall_it : listObstacles)
       {
           int iwall = 0;
           for (auto it = wall_it.begin(); next(it) != wall_it.end(); ++it)
           {
               auto [dist, closestPoint] = get_distance_to_wall_and_closest_point(*it, *(next(it)), posshape);
   
               double2 r_iw = posshape - closestPoint;   //  Vector starting on the wall and going towards the shape
               double distance = dist;
               double2 n_iw;
               if (distance == 0.)
                   n_iw = double2(0., 0.);
               else
                   n_iw = (1. / distance) * r_iw;
               double h = radius[cpt_shape] - distance;
               double2 dcGshape = -(radius[cpt_shape] - h / 2.) * n_iw;
               double2 dcG = delta[cpt_shape] + dcGshape;   //  Distance from the CM G to the contact point c
   
               //  If the shape is in contact with the wall:
               if (h > 0.)
               {
                   double2 v_ci = velshape + (angvel ^ dcGshape);
                   double2 viw = v_ci - double2(0., 0.);
                   double2 vortho_iw = (viw % n_iw) * n_iw;
                   double2 vt_iw = viw - vortho_iw;
                   double norm_vt_iw = !vt_iw;
   
                   //  If the map does not contain this pair ie the slip is not initialized, we initialize it
                   //  Otherwise: we increment it
                   if (!slip_wall.contains({cpt_shape, iobs, iwall}))
                       slip_wall[{cpt_shape, iobs, iwall}] = double2(0., 0.);
                   else
                       slip_wall[{cpt_shape, iobs, iwall}] = slip_wall[{cpt_shape, iobs, iwall}] + dt_mech * vt_iw;
                   //  For the Interactions output file:
                   interactionsOutputWall[{cpt_shape, iobs, iwall}][SLIP] = slip_wall[{cpt_shape, iobs, iwall}];
   
                   double2 delta_tiw = slip_wall[{cpt_shape, iobs, iwall}];
                   double norm_delta_tiw = !delta_tiw;
   
                   double2 t_viw;
                   if (norm_vt_iw > 0)
                       t_viw = (1. / norm_vt_iw) * vt_iw;
                   else if (norm_delta_tiw > 0)
                       t_viw = (1. / norm_delta_tiw) * delta_tiw;
                   else
                       t_viw = double2(0., 0.);
   
                   uint32_t shapeMaterialId = shapesMaterial[active_shapeIDshape_crowd[cpt_shape]];
                   uint32_t obstacleMaterialId = obstaclesMaterial[iobs];
                   /*  Normal interactions  */
                   double k_n_wall = binaryProperties[STIFFNESS_NORMAL][shapeMaterialId][obstacleMaterialId];
                   double Gamma_n_wall = binaryProperties[DAMPING_NORMAL][shapeMaterialId][obstacleMaterialId];
                   double2 fniw_elastic = k_n_wall * h * n_iw;
                   double2 fniw_viscous = -Gamma_n_wall * vortho_iw;
                   double2 fniw = fniw_elastic + fniw_viscous;
                   fortho = fortho + fniw;
                   interactionsOutputWall[{cpt_shape, iobs, iwall}][FORCE_ORTHO] = fniw;
   
                   /*  Tangential interactions  */
                   double k_t_wall = binaryProperties[STIFFNESS_TANGENTIAL][shapeMaterialId][obstacleMaterialId];
                   double Gamma_t_wall = binaryProperties[DAMPING_TANGENTIAL][shapeMaterialId][obstacleMaterialId];
                   double2 ftiw_spring = -k_t_wall * norm_delta_tiw * t_viw;
                   double2 ftiw_viscous = -Gamma_t_wall * vt_iw;
                   double2 ftiw_static = ftiw_spring + ftiw_viscous;
                   double mu_dyn_wall = binaryProperties[FRICTION_SLIDING][shapeMaterialId][obstacleMaterialId];
                   double2 ftiw_dynamic = -mu_dyn_wall * !fniw * t_viw;
                   double2 ftiw = -1. * fmin(!ftiw_static, !ftiw_dynamic) * t_viw;
                   ft = ft + ftiw;
                   interactionsOutputWall[{cpt_shape, iobs, iwall}][FORCE_TAN] = ftiw;
   
                   /*  Torque  */
                   double torqniw = (1. ^ dcG) % fniw;
                   double torqtiw = (1. ^ dcG) % ftiw;
                   double torqiw = torqniw + torqtiw;
                   torq = torq + torqiw;
               }
               iwall++;
           }
           iobs++;
       }
       return {fortho, ft, torq};
   }
   
   void MechanicalLayer::loop()
   {
       //  Reset the forces and torques
       for (unsigned cpt_agent = 0; cpt_agent < nb_active_agents; cpt_agent++)
       {
           Forthon[cpt_agent] = double2(0., 0.);
           Ftn[cpt_agent] = double2(0., 0.);
           taun[cpt_agent] = 0.;
       }
   
       //  Loop over shapes for forces and momentum
       //  Calculation is done at time n
       for (unsigned cpt_shape = 0; cpt_shape < nb_active_shapes; cpt_shape++)
       {
           auto Motion = get_interactions(cpt_shape, true);
           const unsigned cpt_agent(active_shapeIDagent[cpt_shape]);
           Forthon[cpt_agent] =   //  Resultant of normal forces (applied on the contact point)
               Forthon[cpt_agent] + (1. / masses[cpt_agent]) * get<0>(Motion);
           Ftn[cpt_agent] =   //  Resultant of tangential forces (applied on the contact point)
               Ftn[cpt_agent] + (1.0 / masses[cpt_agent]) * get<1>(Motion);
           taun[cpt_agent] = taun[cpt_agent] + (1.0 / mois[cpt_agent]) * get<2>(Motion);   //  Resultant of torques
       }
   
       //  Loop over agents for positions
       for (unsigned cpt_agent = 0; cpt_agent < nb_active_agents; cpt_agent++)
       {
           double UnmZetadt2 = 1.0 - 0.5 * dt_mech * damping[cpt_agent].first;
           taun[cpt_agent] = taun[cpt_agent] + (wdesired[cpt_agent] - wn[cpt_agent]) * damping[cpt_agent].second;
           //  Update positions with velocity Verlet algorithm
           rgnp1[cpt_agent] = rgn[cpt_agent] + UnmZetadt2 * dt_mech * vgn[cpt_agent] +
                              0.5 * dt_mech * dt_mech * (Fp[cpt_agent] + Forthon[cpt_agent] + Ftn[cpt_agent]);
           thetnp1[cpt_agent] = thetn[cpt_agent] + dt_mech * wn[cpt_agent] + 0.5 * dt_mech * dt_mech * taun[cpt_agent];
       }
   
       //  Loop over shapes for velocities
       //  Calculation is done at time n+1
       vector<double2> forthonp1(nb_active_agents, double2(0, 0));
       vector<double2> ftnp1(nb_active_agents, double2(0, 0));
       vector<double> taunp1(nb_active_agents, 0.);
   
       for (unsigned cpt_shape = 0; cpt_shape < nb_active_shapes; cpt_shape++)
       {
           auto Motion = get_interactions(cpt_shape, false);
           const unsigned cpt_agent(active_shapeIDagent[cpt_shape]);
           forthonp1[cpt_agent] = forthonp1[cpt_agent] + get<0>(Motion);
           ftnp1[cpt_agent] = ftnp1[cpt_agent] + get<1>(Motion);
           taunp1[cpt_agent] = taunp1[cpt_agent] + get<2>(Motion);
       }
   
       //  Loop over agents for velocities
       for (unsigned cpt_agent = 0; cpt_agent < nb_active_agents; cpt_agent++)
       {
           double UnmZetadt2 = 1.0 - 0.5 * dt_mech * damping[cpt_agent].first;
           double UnpZetadt2 = 1.0 + 0.5 * dt_mech * damping[cpt_agent].first;
           taunp1[cpt_agent] = taunp1[cpt_agent] + (wdesired[cpt_agent] - wnp1[cpt_agent]) * damping[cpt_agent].second;
           //  Update velocities
           vgnp1[cpt_agent] =
               1.0 / UnpZetadt2 *
               (UnmZetadt2 * vgn[cpt_agent] +
                0.5 * dt_mech * (2. * Fp[cpt_agent] + Forthon[cpt_agent] + Ftn[cpt_agent] + forthonp1[cpt_agent] + ftnp1[cpt_agent]));
           wnp1[cpt_agent] = wn[cpt_agent] + 0.5 * dt_mech * (taun[cpt_agent] + taunp1[cpt_agent]);
       }
   
       //  Update relative positions of the shapes
       for (unsigned cpt_shape = 0; cpt_shape < nb_active_shapes; cpt_shape++)
       {
           const unsigned cpt_agent(active_shapeIDagent[cpt_shape]);
           const double delta_theta = thetnp1[cpt_agent] - thetn[cpt_agent];
           delta[cpt_shape].first = delta[cpt_shape].first * cos(delta_theta) - delta[cpt_shape].second * sin(delta_theta);
           delta[cpt_shape].second = delta[cpt_shape].first * sin(delta_theta) + delta[cpt_shape].second * cos(delta_theta);
       }
   
       //  Update position, velocity, orientation, angular velocity of each agent
       for (unsigned cpt_agent = 0; cpt_agent < nb_active_agents; cpt_agent++)
       {
           {
               rgn[cpt_agent] = rgnp1[cpt_agent];
               vgn[cpt_agent] = vgnp1[cpt_agent];
               thetn[cpt_agent] = thetnp1[cpt_agent];
               wn[cpt_agent] = wnp1[cpt_agent];
           }
       }
   }
   
   pair<bool, bool> MechanicalLayer::existsContacts()
   {
       bool agentContact = false;
       bool wallContact = false;
   
       for (auto const& [key, value] : slip)
       {
           if (value != double2(0., 0.))
           {
               agentContact = true;
               break;
           }
       }
       for (auto const& [key, value] : slip_wall)
       {
           if (value != double2(0., 0.))
           {
               wallContact = true;
               break;
           }
       }
       return {agentContact, wallContact};
   }
   
   void MechanicalLayer::generateInteractionsOutputFile(const string& interactionsFile, const pair<bool, bool>& exists)
   {
       ofstream outputDoc;
       outputDoc.open(interactionsFile);
   
       outputDoc << R"(<?xml version="1.0" encoding="utf-8"?>)" << endl;
       outputDoc << "<Interactions>" << endl;
       if (!exists.first && !exists.second)
       {
           outputDoc << "</Interactions>";
           return;
       }
   
       /*  Loop over active agents */
       set<unsigned> parent;                        //  Variable to remember if we have opening tags for parents
       set<pair<unsigned, unsigned>> parentChild;   //  Variable to remember if we have an opening child tag
       for (uint32_t a = 0; a < nb_active_agents; a++)
       {
           //  First, collisions with agents
           if (exists.first && !interactionsOutput.empty())
           {
               for (auto iterator = interactionsOutput.begin(); iterator != interactionsOutput.end();)
               {
                   auto shape = iterator->first.first;
                   const uint32_t agent = active_shapeIDagent[shape];
                   if (agent > a)
                       break;
                   //  If we're here, agent = a
                   auto output = iterator->second;
                   if (output[SLIP] == double2(0., 0.) && output[FORCE_ORTHO] == double2(0., 0.) && output[FORCE_TAN] == double2(0., 0.))
                       continue;
                   if (!parent.contains(a))
                   {
                       if (!parent.empty())
                           outputDoc << "    </Agent>" << endl;
                       outputDoc << "    <Agent Id=\"" << agentMapInverse[agentActiveIds[agent]] << "\">" << endl;
                       parent.insert(a);
                   }
                   auto shapeNeighbour = iterator->first.second;
                   const uint32_t neighbour = active_shapeIDagent[shapeNeighbour];
                   if (!parentChild.contains({agent, neighbour}))
                   {
                       if (!parentChild.empty() && parentChild.rbegin()->first == agent)
                           //  We have switched to another child within the same agent -> insert child closing tag
                           outputDoc << "        </Agent>" << endl;
                       outputDoc << "        <Agent Id=\"" << agentMapInverse[agentActiveIds[neighbour]] << "\">" << endl;
                       parentChild.insert({agent, neighbour});
                   }
                   outputDoc << "            <Interaction ParentShape=\"" << (shape - agentIDshape[agent]) << "\" "
                             << "ChildShape=\"" << (shapeNeighbour - agentIDshape[neighbour]) << "\" ";
                   if (output[SLIP] != double2(0., 0.))
                       outputDoc << "TangentialRelativeDisplacement=\"" << output[SLIP].first << "," << output[SLIP].second << "\" ";
                   if (output[FORCE_ORTHO] != double2(0., 0.))
                       outputDoc << "Fn=\"" << output[FORCE_ORTHO].first << "," << output[FORCE_ORTHO].second << "\" ";
                   if (output[FORCE_TAN] != double2(0., 0.))
                       outputDoc << "Ft=\"" << output[FORCE_TAN].first << "," << output[FORCE_TAN].second << "\" ";
                   outputDoc << "/>" << endl;
                   interactionsOutput.erase(iterator++);
               }
               if (!parentChild.empty() && parentChild.rbegin()->first == a)
                   //  If there were entries for the current agent, we need to close the last Agent child
                   outputDoc << "        </Agent>" << endl;
           }
           //  Second, collision with walls
           if (exists.second && !interactionsOutputWall.empty())
           {
               for (auto iterator = interactionsOutputWall.begin(); iterator != interactionsOutputWall.end();)
               {
                   auto key = iterator->first;
                   const uint32_t shape = get<0>(key);
                   const uint32_t agent = active_shapeIDagent[shape];
                   //  If the current element of interactionsOutputWall is not the same as the last parent, end
                   if (agent > a)
                       break;
                   auto output = iterator->second;
                   if (output[0] == double2(0., 0.) && output[1] == double2(0., 0.) && output[2] == double2(0., 0.))
                       continue;
                   if (!parent.contains(a))
                   {
                       if (!parent.empty())
                           outputDoc << "    </Agent>" << endl;
                       outputDoc << "    <Agent Id=\"" << agentMapInverse[agentActiveIds[agent]] << "\">" << endl;
                       parent.insert(a);
                   }
                   outputDoc << "        <Wall ShapeId=\"" << (shape - agentIDshape[agent]) << "\" "
                             << "WallId=\"" << get<1>(key) << "\" CornerId=\"" << get<2>(key) << "\" ";
                   if (output[SLIP] != double2(0., 0.))
                       outputDoc << "TangentialRelativeDisplacement=\"" << output[SLIP].first << "," << output[SLIP].second << "\" ";
                   if (output[FORCE_TAN] != double2(0., 0.))
                       outputDoc << "Ft=\"" << output[FORCE_TAN].first << "," << output[FORCE_TAN].second << "\" ";
                   if (output[FORCE_ORTHO] != double2(0., 0.))
                       outputDoc << "Fn=\"" << output[FORCE_ORTHO].first << "," << output[FORCE_ORTHO].second << "\" ";
                   outputDoc << "/>" << endl;
                   //  Erase the entry in slip_wall to make the next sequential search "easier"
                   interactionsOutputWall.erase(iterator++);
               }
           }
       }
       outputDoc << "    </Agent>" << endl;
       outputDoc << "</Interactions>";
   
       outputDoc.close();
   }
