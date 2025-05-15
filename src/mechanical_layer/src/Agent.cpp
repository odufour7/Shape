/*
   Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
   Agent.cpp contains the constructor of the agent class, as well as functions related to the agent's properties.
 */

#include "Agent.h"

#include <utility>
#include <vector>

using std::vector;

#if !defined(DOXYGEN_SHOULD_SKIP_THIS)
/**
 * @brief Calculates the size of the body of the agent.
 * The size is defined as the radius of the smallest circle containing all the shapes.
 *
 * @param delta_gtos The vector of delta_gtos', ie the shapes' positions relative to the agent's center of mass
 * @param radius_shapes The vector of radius_shapes, ie the radii of the agent's shapes.
 *
 * @return The size of the body of the agent.
 */
static double size_body(const vector<double2>& delta_gtos, const vector<double>& radius_shapes)
{
    double max_delta_gtos = 0.0;
    size_t cpt_max = 0;
    for (size_t i = 0; i < delta_gtos.size(); ++i)
    {
        if (const double magnitude = !delta_gtos[i]; magnitude > max_delta_gtos)
        {
            max_delta_gtos = magnitude;
            cpt_max = i;
        }
    }
    double radius(radius_shapes[cpt_max]);
    if (radius_shapes[cpt_max] < 0.0)
    {
        radius = -radius_shapes[cpt_max];
    }
    return radius + max_delta_gtos;
}
#endif   // DOXYGEN_SHOULD_SKIP_THIS

/**
 * @brief Constructor for the Agent class.
 *
 * @param ID The ID of the agent.
 * @param Ids_shapes The Ids of the shapes
 * @param x The initial x-coordinate of the agent.
 * @param y The initial y-coordinate of the agent.
 * @param vx The initial x-velocity of the agent.
 * @param vy The initial y-velocity of the agent.
 * @param omega The initial angular speed of the agent.
 * @param Fp
 * @param Mp
 * @param nb_shapes The number of shapes.
 * @param delta_gtos Vector of delta gtos.
 * @param radius_shapes Vector of shape radii.
 * @param theta_body The orientation of the agent's body.
 * @param theta_body_init
 * @param mass
 * @param moi
 */
Agent::Agent(unsigned ID, vector<unsigned> Ids_shapes, double x, double y, double vx, double vy, double omega, double2 Fp, double Mp,
             unsigned nb_shapes, const vector<double2>& delta_gtos, const vector<double>& radius_shapes, double theta_body,
             double theta_body_init, double mass, double moi)
    : _id(ID),
      _mass(mass),
      _moi(moi),
      _ids_shapes(std::move(Ids_shapes)),
      _radius(size_body(delta_gtos, radius_shapes)),
      _nb_shapes(nb_shapes),
      _delta_gtos(delta_gtos),
      _radius_shapes(radius_shapes),
      _theta_init(theta_body_init),
      _x(x),
      _y(y),
      _theta(theta_body),
      _vx(vx),
      _vy(vy),
      _w(omega)
{
    const double inverseTauMechTranslation = agentProperties[_id].first;
    const double inverseTauMechRotation = agentProperties[_id].second;
    _vx_des = Fp.first / inverseTauMechTranslation / _mass;    //  vx_des := Fpx/m * tau_mech
    _vy_des = Fp.second / inverseTauMechTranslation / _mass;   //  vy_des := Fpy/m * tau_mech
    _w_des = Mp / inverseTauMechRotation / _moi;               //  w_des  := Mp/I  * tau_mech

    if (!(_vx_des == 0. && _vy_des == 0.))
        _theta_des = atan2(_vy_des, _vx_des);
    else
        _theta_des = 0.;
    _v_des = double2(_vx_des, _vy_des);
}

/**
 * @brief Destructor for the Agent class.
 *
 * This destructor is responsible for cleaning up any resources allocated by an Agent object.
 * It is automatically called when an Agent object goes out of scope or is explicitly deleted.
 */
Agent::~Agent() = default;

/**
 * @brief Moves the agent based on its velocity and angular velocity.
 *
 * This function updates the position and orientation of the agent based on its current velocity (_vx, _vy)
 * and angular velocity (_w). The movement is performed over a small time interval (dt).
 */
void Agent::move()
{
    _x += _vx * dt;
    _y += _vy * dt;
    _theta += _w * dt;
}

/**
 * @brief Calculates the current relative positions of the shapes
 *
 * Based on the current orientation of the agent wrt the x-axis, this function gives
 * the relative positions of the agent's shapes.
 *
 * @return The updated relative positions of the shapes
 */
vector<double2> Agent::get_delta_gtos()
{
    vector<double2> delta_gtos_abs;
    for (auto [x, y] : _delta_gtos)
    {
        const double rotation_angle = _theta - _theta_init;
        delta_gtos_abs.emplace_back(x * cos(rotation_angle) - y * sin(rotation_angle),
                                    x * sin(rotation_angle) + y * cos(rotation_angle));
    }
    return delta_gtos_abs;
}
