
.. _program_listing_file_include_Agent.h:

Program Listing for File Agent.h
================================

|exhale_lsh| :ref:`Return to documentation for file <file_include_Agent.h>` (``include/Agent.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   /*
       Copyright  2025  Institute of Light and Matter, CNRS UMR 5306
       Contributors: Oscar DUFOUR, Maxime STAPELLE, Alexandre NICOLAS
   
       This software is a computer program designed to generate a realistic crowd from anthropometric data and
       simulate the mechanical interactions that occur within it and with obstacles.
   
       This software is governed by the CeCILL  license under French law and abiding by the rules of distribution
       of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL
       license as circulated by CEA, CNRS and INRIA at the following URL "http://www.cecill.info".
   
       As a counterpart to the access to the source code and  rights to copy, modify and redistribute granted by
       the license, users are provided only with a limited warranty  and the software's author,  the holder of the
       economic rights,  and the successive licensors  have only  limited liability.
   
       In this respect, the user's attention is drawn to the risks associated with loading,  using,  modifying
       and/or developing or reproducing the software by the user in light of its specific status of free software,
       that may mean  that it is complicated to manipulate,  and  that  also therefore means  that it is reserved
       for developers  and  experienced professionals having in-depth computer knowledge. Users are therefore
       encouraged to load and test the software's suitability as regards their requirements in conditions enabling
       the security of their systems and/or data to be ensured and,  more generally, to use and operate it in the
       same conditions as regards security.
   
       The fact that you are presently reading this means that you have had knowledge of the CeCILL license and that
       you accept its terms.
   */
   
   #ifndef SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
   #define SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
   
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
       Agent(unsigned ID, std::vector<unsigned> Ids_shapes, unsigned nb_shapes, const std::vector<double2>& delta_gtos,
             const std::vector<double>& radius_shapes, double theta_body_init, double mass, double moi);
       ~Agent();
   
       void move();
       inline double2 get_r() { return {_x, _y}; }
       inline double2 get_v() { return {_vx, _vy}; }
       std::vector<double2> get_delta_gtos();
   };
   
   #endif   // SRC_MECHANICAL_LAYER_INCLUDE_AGENT_H_
