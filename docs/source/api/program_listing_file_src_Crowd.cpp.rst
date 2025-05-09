
.. _program_listing_file_src_Crowd.cpp:

Program Listing for File Crowd.cpp
==================================

|exhale_lsh| :ref:`Return to documentation for file <file_src_Crowd.cpp>` (``src/Crowd.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
       Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
       Crowd.cpp is responsible for setting up the global situation, decide which agents
       are mechanically active and call the mechanical layer for the latter.
    */
   
   #include "Crowd.h"
   
   #include <iostream>
   #include <list>
   #include <string>
   #include <vector>
   
   #include "MechanicalLayer.h"
   
   using std::string, std::vector, std::list, std::cerr, std::cout, std::endl, std::ranges::find, std::ofstream;
   
   //  Global variable: Mechanically active agents
   list<Agent*> mech_active_agents;
   
   int initialiseSetting(const std::string& dynamicsFile, std::vector<unsigned>& nb_shapes_allagents, std::vector<unsigned>& shapeIDagent,
                         std::vector<int>& edges, std::vector<double>& radius_allshapes, std::vector<double>& masses,
                         std::vector<double>& mois, std::vector<double2>& delta_gtos)
   {
       /*  Allocate agents */
       agents = new Agent*[nAgents];
   
       /*  Create ids of shapes for agents */
       vector<unsigned> Id_shapes(shapeIDagent.size());
       for (size_t i = 0; i < shapeIDagent.size(); i++)
       {
           Id_shapes[i] = i;
       }
   
       /*  Create agents: read the dynamics file first  */
       tinyxml2::XMLDocument document;
       document.LoadFile(dynamicsFile.data());
       if (document.ErrorID() != 0)
       {
           cerr << "Error: Could not load or parse XML file " << dynamicsFile << endl;
           return EXIT_FAILURE;
       }
       //  Read the Agents block
       tinyxml2::XMLElement* agentsElement = document.FirstChildElement("Agents");
       if (!agentsElement)
       {
           cerr << "Error: agents must be embedded in \"Agents\" tag!" << endl;
           return EXIT_FAILURE;
       }
       const tinyxml2::XMLElement* agentElement = agentsElement->FirstChildElement("Agent");
       if (!agentElement)
       {
           cerr << "Error: no Agent tag present in " << dynamicsFile << endl;
           return EXIT_FAILURE;
       }
       uint32_t agentCounter = 0;
       while (agentElement != nullptr)
       {
           const char* agentId = nullptr;
           uint32_t a;
           agentElement->QueryStringAttribute("Id", &agentId);
           if (!agentId)
           {
               cerr << "Error: agent tag with no id in dynamics file" << endl;
               return EXIT_FAILURE;
           }
           if (!agentMap.contains(agentId))
           {
               cerr << "Error: unknown agent " << agentId << " in dynamics file" << endl;
               return EXIT_FAILURE;
           }
           else
           {
               a = agentMap[agentId];
           }
   
           const unsigned ID_agent(a);
           vector<double2> delta_gtos_curr(&delta_gtos[edges[a]], &delta_gtos[edges[a + 1]]);
           double2 shoulders_direction(delta_gtos[edges[a + 1] - 1] - delta_gtos[edges[a]]);    // from left to right
           double2 orientation_vec({-shoulders_direction.second, shoulders_direction.first});   // normal to the shoulders direction
           double theta_body_init(0.);
           if (!(orientation_vec.first == 0. && orientation_vec.second == 0.))
               theta_body_init = atan2(orientation_vec.second, orientation_vec.first);
   
           vector<double> radius_shapes(&radius_allshapes[edges[a]], &radius_allshapes[edges[a + 1]]);
           const vector<unsigned> Ids_shapes_agent(&Id_shapes[edges[a]], &Id_shapes[edges[a + 1]]);
           const double mass_curr(masses[a]), moi_curr(mois[a]);
   
           //  Kinematics and Dynamics
           const tinyxml2::XMLElement* kinematicsElement = agentElement->FirstChildElement("Kinematics");
           if (!kinematicsElement)
           {
               cerr << "Error: no Kinematics tag present for agent " << agentId << endl;
               return EXIT_FAILURE;
           }
           const char* buffer = nullptr;
           if (kinematicsElement->QueryStringAttribute("Position", &buffer) != tinyxml2::XML_SUCCESS)
           {
               cerr << "Error: Could not parse agent position from XML file " << dynamicsFile << endl;
               return EXIT_FAILURE;
           }
           auto [rcPosition, position] = parse2DComponents(buffer);
           if (rcPosition != EXIT_SUCCESS)
           {
               cerr << "Error: Could not parse corner coordinates from XML file " << dynamicsFile << endl;
               return EXIT_FAILURE;
           }
   
           if (kinematicsElement->QueryStringAttribute("Velocity", &buffer) != tinyxml2::XML_SUCCESS)
           {
               cerr << "Error: Could not parse agent velocity from XML file " << dynamicsFile << endl;
               return EXIT_FAILURE;
           }
           auto [rcVelocity, velocity] = parse2DComponents(buffer);
           if (rcVelocity != EXIT_SUCCESS)
           {
               cerr << "Error: Could not parse corner coordinates from XML file " << dynamicsFile << endl;
               return EXIT_FAILURE;
           }
           double theta, omega;
           if (kinematicsElement->QueryDoubleAttribute("theta", &theta) != tinyxml2::XML_SUCCESS)
               cerr << "Error: could not get orientation of agent " << agentId << endl;
           if (kinematicsElement->QueryDoubleAttribute("omega", &omega) != tinyxml2::XML_SUCCESS)
               cerr << "Error: could not get angular velocity of agent " << agentId << endl;
   
           const tinyxml2::XMLElement* dynamicsElement = agentElement->FirstChildElement("Dynamics");
           if (!dynamicsElement)
           {
               cerr << "Error: no Dynamics tag present for agent " << agentId << endl;
               return EXIT_FAILURE;
           }
           if (dynamicsElement->QueryStringAttribute("Fp", &buffer) != tinyxml2::XML_SUCCESS)
           {
               cerr << "Error: could not get driving force of agent " << agentId << endl;
               return EXIT_FAILURE;
           }
           auto [rcFp, Fp] = parse2DComponents(buffer);
           if (rcFp != EXIT_SUCCESS)
           {
               cerr << "Error: Could not parse corner coordinates from XML file " << dynamicsFile << endl;
               return EXIT_FAILURE;
           }
           double Mp;
           if (dynamicsElement->QueryDoubleAttribute("Mp", &Mp) != tinyxml2::XML_SUCCESS)
           {
               cerr << "Error: could not get driving torque of agent " << agentId << endl;
               return EXIT_FAILURE;
           }
           //  Actual creation of the Agent object
           agents[ID_agent] =
               new Agent(ID_agent, Ids_shapes_agent, position.first, position.second, velocity.first, velocity.second, omega, Fp, Mp,
                         nb_shapes_allagents[a], delta_gtos_curr, radius_shapes, theta, theta_body_init, mass_curr, moi_curr);
   
           agentElement = agentElement->NextSiblingElement("Agent");
           agentCounter++;
       }
       //  Check if the number of agents in the Dynamics file is the same as in the Agents file
       if (agentCounter != nAgents)
       {
           cerr << "Not all agents are present in the dynamics file" << dynamicsFile << endl;
           return EXIT_FAILURE;
       }
   
       /*  Update neighbours before calling the mechanical layer   */
       determine_agents_neighbours();
   
       return EXIT_SUCCESS;
   }
   
   void determine_agents_neighbours()
   {
       const double criticalDistanceWall = dt * vMaxAgent;
       const double criticalDistance = 2 * criticalDistanceWall;
   
       for (uint32_t a1 = 0; a1 < nAgents; a1++)
       {
           Agent* agent1 = agents[a1];
           //  First, check walls
           for (uint32_t iobs = 0; iobs < listObstacles.size(); iobs++)
           {
               for (uint32_t iwall = 0; iwall < listObstacles[iobs].size() - 1; iwall++)
               {
                   auto [distance, closest_point] = get_distance_to_wall_and_closest_point(
                       listObstacles[iobs][iwall], listObstacles[iobs][iwall + 1], agent1->get_r());
                   if (distance < criticalDistanceWall)
                       agent1->_neighbours_walls.emplace_back(iobs, iwall);
               }
           }
           //  Then, other agents
           for (uint32_t a2 = a1 + 1; a2 < nAgents; a2++)
           {
               Agent* agent2 = agents[a2];
   
               const double2 r1 = agent1->get_r();
               const double2 r2 = agent2->get_r();
               if (const double r = get_distance(r1, r2); r < criticalDistance)
               {
                   agent1->_neighbours.push_back(agent2->_id);
                   agent2->_neighbours.push_back(agent1->_id);
               }
           }
       }
   }
   
   void handleMechanicalLayer(const std::string& dynamicsFile)
   {
       /*  Handle mechanically active agents: mechanical layer */
       if (get_future_collision())
       {
           const MechanicalLayer* crowdMech = new MechanicalLayer(mech_active_agents);
           delete crowdMech;
       }
   
       /*  Handle non mechanically active agents: simple positional update */
       for (uint32_t a = 0; a < nAgents; a++)
       {
           Agent* agent = agents[a];
           if (is_mechanically_active(agent))
               continue;
           const double inverseTauMechTranslation = agentProperties[agent->_id].first;
           const double inverseTauMechRotation = agentProperties[agent->_id].second;
           agent->_vx = (1.0 - exp(-dt * inverseTauMechTranslation)) * agent->_vx_des + exp(-dt * inverseTauMechTranslation) * agent->_vx;
           agent->_vy = (1.0 - exp(-dt * inverseTauMechTranslation)) * agent->_vy_des + exp(-dt * inverseTauMechTranslation) * agent->_vy;
           agent->_w = (1.0 - exp(-dt * inverseTauMechRotation)) * agent->_w_des + exp(-dt * inverseTauMechRotation) * agent->_w;
           agent->move();
       }
   
       /*  Save output of mechanical layer to file */
       generateDynamicsOutputFile(dynamicsFile);
   }
   
   bool is_mechanically_active(const Agent* agent) { return (find(mech_active_agents, agent) != mech_active_agents.end()); }
   
   bool get_future_collision()
   {
       //  Test new positions
       for (uint32_t a = 0; a < nAgents; a++)
       {
           Agent* agent = agents[a];
   
           agent->_x += agent->_vx_des * dt;
           agent->_y += agent->_vy_des * dt;
           agent->_theta += agent->_w_des * dt;
       }
   
       //  Check if overlaps
       mech_active_agents.clear();
       for (uint32_t a = 0; a < nAgents; a++)
       {
           Agent* agent1 = agents[a];
           //  Loop over current agent's wall neighbours
           for (const auto& [iobs, iwall] : agent1->_neighbours_walls)
           {
               double2 middlePointWall = 0.5 * (listObstacles[iobs][iwall] + listObstacles[iobs][iwall + 1]);
               if ((!(agent1->get_r() - middlePointWall)) < agent1->_radius + 1e-1)
                   if (!is_mechanically_active(agent1))
                       mech_active_agents.push_back(agent1);
           }
           //  Loop over current agent's neighbours
           for (const unsigned agent2_id : agent1->_neighbours)
           {
               if (Agent* agent2 = agents[agent2_id];
                   (!(agent1->get_r() - agent2->get_r())) < fabs(agent1->_radius + agent2->_radius) + 1e-1)
               {
                   if (!is_mechanically_active(agent1))
                       mech_active_agents.push_back(agent1);
                   if (!is_mechanically_active(agent2))
                       mech_active_agents.push_back(agent2);
               }
           }
       }
   
       //  Revert to former positions
       for (uint32_t a = 0; a < nAgents; a++)
       {
           Agent* agent = agents[a];
   
           agent->_x -= agent->_vx_des * dt;
           agent->_y -= agent->_vy_des * dt;
           agent->_theta -= agent->_w_des * dt;
       }
   
       //  Add agents with significant velocity changes
       for (uint32_t a = 0; a < nAgents; a++)
       {
           if (Agent* agent = agents[a];
               pow(agent->_vx - agent->_vx_des, 2) + pow(agent->_vy - agent->_vy_des, 2) + pow(agent->_w - agent->_w_des, 2) > 1e-4 &&
               !is_mechanically_active(agent))
               mech_active_agents.push_back(agent);
       }
   
       //  Add neighbours of active agents
       for (const Agent* agent : mech_active_agents)
       {
           for (const unsigned neighbour : agent->_neighbours)
           {
               if (!is_mechanically_active(agents[neighbour]))
                   mech_active_agents.push_back(agents[neighbour]);
           }
       }
       return (!mech_active_agents.empty());
   }
   
   void generateDynamicsOutputFile(const std::string& dynamicsFile)
   {
       //  We'll  build the output from the input (the structure and fields are exactly the same)
       tinyxml2::XMLDocument inputDoc;
       inputDoc.LoadFile((dynamicsFile).data());
       ofstream outputDoc;
       outputDoc.open(dynamicsFile);
   
       outputDoc << R"(<?xml version="1.0" encoding="utf-8"?>)" << endl;
       //  Read the Agents block
       tinyxml2::XMLElement* InAgentsElement = inputDoc.FirstChildElement("Agents");
       outputDoc << "<Agents>" << endl;
   
       const tinyxml2::XMLElement* InAgentElement = InAgentsElement->FirstChildElement("Agent");
       while (InAgentElement != nullptr)
       {
           //  First, get our internal id
           const char* agentId = nullptr;
           InAgentElement->QueryStringAttribute("Id", &agentId);
           const uint32_t a = agentMap[agentId];
           struct Agent* agent = agents[a];
           outputDoc << "    <Agent Id=\"" << agentId << "\">" << endl;
           //  Kinematics
           outputDoc << "        <Kinematics Position=\"" << agent->_x << "," << agent->_y << "\" ";
           outputDoc << "Velocity=\"" << agent->_vx << "," << agent->_vy << "\" ";
           outputDoc << "theta=\"" << agent->_theta << "\" omega=\"" << agent->_w << "\"/>" << endl;
   
           InAgentElement = InAgentElement->NextSiblingElement("Agent");
           outputDoc << "    </Agent>" << endl;
       }
       outputDoc << "</Agents>";
   
       outputDoc.close();
   }
