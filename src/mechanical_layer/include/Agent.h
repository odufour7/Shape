/* Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */

#ifndef SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
#define SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_

#include <list>
#include <utility>
#include <vector>

#include "Global.h"

struct Agent
/**
 * @brief Class representing an agent in the simulation.
 *
 * This class defines the properties and behaviors of an agent, such as its position, velocity, and shape.
 * Agents can interact with each other and navigate through the environment based on a driving force.
 */
{
    const unsigned _id;                        ///< Agent id
    const double _mass;                        ///<  Mass
    const double _moi;                         ///<  Moment of inertia
    const std::vector<unsigned> _ids_shapes;   ///<  List of ids of the shapes of the agent
    const double _radius;                      ///<  Equivalent radius for repulsive force
    const unsigned _nb_shapes;                 ///< Number of shapes of the agent
    std::vector<double2> _delta_gtos;   ///<  List of vector from the center of mass G to the center of each physical shape (disc)

    const std::vector<double> _radius_shapes;   ///<  The radii of the agent's shapes
    /// The initial value of the agent's orientation, derived from the relative positions of its shapes in the Agents XML file.
    const double _theta_init;
    double _x;           ///< x-component of the center of mass
    double _y;           ///< y-component of the center of mass
    double _theta;       ///< Orientation of the agent
    double _vx;          ///< x-component of the velocity of the center of mass
    double _vy;          ///< y-component of the velocity of the center of mass
    double _w;           ///<  Angular velocity of the agent
    double _vx_des;      ///<  x-component of the desired velocity of the agent
    double _vy_des;      ///<  y-component of the desired velocity of the agent
    double _w_des;       ///<  Desired angular velocity of the agent
    double _theta_des;   ///<  Desired orientation of the agent (orientation of the desired velocity)

    double2 _v_des;                                               ///< Norm (N2) of the desired velocity
    std::list<unsigned> _neighbours;                              ///<  List of neighbours
    std::list<std::pair<unsigned, unsigned>> _neighbours_walls;   ///<  List of neighbouring walls

    /*  Constructor for the class   */
    Agent(unsigned ID, std::vector<unsigned> Ids_shapes, unsigned nb_shapes, const std::vector<double2>& delta_gtos,
          const std::vector<double>& radius_shapes, double theta_body_init, double mass, double moi);
    ~Agent();

    void move();
    /**
     * @brief The method gets the current position of the agent
     *
     * @returns The position in cartesian coordinates as a double2
     */
    inline double2 get_r() { return {_x, _y}; }
    /**
     * @brief The method gets the current velocity of the agent
     *
     * @returns The velocity in cartesian coordinates as a double2
     */
    inline double2 get_v() { return {_vx, _vy}; }
    std::vector<double2> get_delta_gtos();
};

#endif   // SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
