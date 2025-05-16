
.. _program_listing_file_src_Agent.cpp:

Program Listing for File Agent.cpp
==================================

|exhale_lsh| :ref:`Return to documentation for file <file_src_Agent.cpp>` (``src/Agent.cpp``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
      Copyright 2025 <Dufour Oscar, Maxime Stappel, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306>
      Agent.cpp contains the constructor of the agent class, as well as functions related to the agent's properties.
    */
   
   #include "Agent.h"
   
   #include <utility>
   #include <vector>
   
   using std::vector;
   
   #if !defined(DOXYGEN_SHOULD_SKIP_THIS)
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
   
   Agent::~Agent() = default;
   
   void Agent::move()
   {
       _x += _vx * dt;
       _y += _vy * dt;
       _theta += _w * dt;
   }
   
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
