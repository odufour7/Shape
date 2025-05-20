/*
 *  Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
 *  "Mechanical layer" for handling agent collisions in agent-based models
 *  Designed as a shared library to be called from Python or C++
 *
 *  Part the agent-based model "ANticipatory Dynamics Algorithm (ANDA)":
 *      - A. Nicolas, 2020
 *      - I. Echeverria, 2021
 *      - O. Dufour, 2024
 *  Adapted as a standalone library by M. Stapelle, 2025.
 *
 */

#include <string>
#include <vector>

#include "CrowdMechanics.h"
using std::string, std::map, std::vector;

//  extern C is a trick for Python ctypes to work
extern "C"
{
    /**
     * @brief The main function of CrowdMechanics, and the only one to be called when used as a library.
     *
     * It reads static and dynamic XML files,
     * stores everything and simulates the dynamics of the agents.
     *
     * @param files An array of file names. They should be given in a precise order:
     *      - Parameters (directories, time step...)
     *      - Materials (with Young's modulus and the shear modulus
     *      - Geometry (obstacles)
     *      - Agents
     *      - Agent dynamics (current kinematics, and driving forces and torques)
     *      - (optional) Agent interactions (the information about agent-to-agent and agent-to-obstacle contacts,
     *                   if any, will be used.
     *
     * @return  EXIT_SUCCESS if the program executed successfully.
     *          EXIT_FAILURE in case of issue(s) with any of the XML files' contents
     */
    int CrowdMechanics(char** files)
    {
        /*  Read general PARAMETERS  */
        if (const string parametersFile = files[0]; readParameters(parametersFile) == EXIT_FAILURE)
            return EXIT_FAILURE;
        //  Store the dynamics file name, wether it is the first run or not
        const string dynamicsFile = pathDynamic + files[4];

        if (firstRun) {
            /*  Read MATERIALS  */
            //  Mapping between user-given id's and indexes in the program
            map<string, int32_t> materialMapping;
            if (const string materialsFile = pathStatic + files[1]; readMaterials(materialsFile, materialMapping) == EXIT_FAILURE)
                return EXIT_FAILURE;

            /*  Read GEOMETRY   */
            if (const string geometryFile = pathStatic + files[2]; readGeometry(geometryFile, materialMapping) == EXIT_FAILURE)
                return EXIT_FAILURE;

            /*  Read AGENTS */
            vector<unsigned> nb_shapes_allagents, shapeIDagent;
            vector<int> edges;
            vector<double> radius_allshapes, masses, mois;
            vector<double2> delta_gtos;
            if (const string agentsFile = pathStatic + files[3];
                readAgents(agentsFile, nb_shapes_allagents, shapeIDagent, edges, radius_allshapes, masses, mois, delta_gtos,
                           materialMapping) == EXIT_FAILURE)
                return EXIT_FAILURE;

            /*  Initialise simulation  */
            if (initialiseSetting(dynamicsFile, nb_shapes_allagents, shapeIDagent, edges, radius_allshapes, masses, mois, delta_gtos) ==
                EXIT_FAILURE)
                return EXIT_FAILURE;
        }
        else
            if (updateSetting(dynamicsFile) == EXIT_FAILURE)
                return EXIT_FAILURE;

        /*  Main program procedure  */
        handleMechanicalLayer(dynamicsFile);

        firstRun = false;
        return EXIT_SUCCESS;
    }
}
