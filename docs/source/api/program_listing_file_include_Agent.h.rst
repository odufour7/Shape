
.. _program_listing_file_include_Agent.h:

Program Listing for File Agent.h
================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_Agent.h>` (``include/Agent.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /* Copyright 2025 <Dufour Oscar, Maxime Stappel, David Rodney, Nicolas Alexandre, Institute of Light and Matter, CNRS UMR 5306> */
   
   #ifndef SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
   #define SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
   
   #include <list>
   #include <utility>
   #include <vector>
   
   #include "Global.h"
   
   struct Agent
   {
       const unsigned _id;                        
       const double _mass;                        
       const double _moi;                         
       const std::vector<unsigned> _ids_shapes;   
       const double _radius;                      
       const unsigned _nb_shapes;                 
       std::vector<double2> _delta_gtos;   
   
       const std::vector<double> _radius_shapes;   
       const double _theta_init;
       double _x;           
       double _y;           
       double _theta;       
       double _vx;          
       double _vy;          
       double _w;           
       double _vx_des;      
       double _vy_des;      
       double _w_des;       
       double _theta_des;   
   
       double2 _v_des;                                               
       std::list<unsigned> _neighbours;                              
       std::list<std::pair<unsigned, unsigned>> _neighbours_walls;   
   
       /*  Constructor for the class   */
       Agent(unsigned ID, std::vector<unsigned> Ids_shapes, double x, double y, double vx, double vy, double omega, double2 Fp, double Mp,
             unsigned nb_shapes, const std::vector<double2>& delta_gtos, const std::vector<double>& radius_shapes, double theta_body,
             double theta_body_init, double mass, double moi);
       ~Agent();
   
       void move();
       inline double2 get_r() { return {_x, _y}; }
       inline double2 get_v() { return {_vx, _vy}; }
       std::vector<double2> get_delta_gtos();
   };
   
   #endif   // SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
