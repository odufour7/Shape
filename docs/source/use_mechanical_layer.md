# Tutorial for the ```CrowdMechanics``` engine

The purpose of the engine is to take a configuration of agents, who may or may not have obstacles around, and evolve their position given driving forces and torques, duly handling possible collisions.

There is a single standalone function to be called, that will take as input a list of XML files names and will produce XML files with the resulting configuration.

There are two types of files: the static ones which contains immutable parameters such as the positions of walls, the characteristics of the materials, ... And the dynamic ones that contain values that change over time, ie the kinematics and dynamics of the agents:

- **Static**:
  - *Parameters* contain technical information such as working directories, but also time intervals of the simulation;
  - *Materials* contain physical information about the materials the agents and obstacles are made of;
  - *Geometry* details the layout of the scene: dimensions and positions of obstacles
  - *Agents* lists the agents and the shapes that constitute them.
- **Dynamic**
  - *Agent Dynamics* contain the current positions and velocities of the agents, as well as the driving forces and torques we apply to them. It is used as input as well as as output of the library.
  - (*optional*) *Agent Interactions* is a product of the library that lists all the contacts, be it agent/agent or agent/obstacle, the forces on each agent as well as a technical quantity that we call the Tangential relative displacement. This file must also be provided as input to the library if the current execution is part of a series of consecutive executions of the same situation.

We detail the contents of those files below, by order of importance and of input into the function.

> Note: we use the external library [tinyxml2](http://leethomason.github.io/tinyxml2/index.html) for the handling of XML files.

## Static information

### Parameters
The layout is the following:
```xml
<?xml version="1.0" encoding="utf-8"?>
<Parameters>
    <Directories Static="/AbsolutePathToStatic/" Dynamic="/AbsolutePathToDynamic/"/>
    <Times TimeStep="0.1" TimeStepMechanical="1e-5"/>
</Parameters>
```
First, note that the Parameters are enclosed in a root *Parameters* tag. This will be the same for each of the XML files.
The expected tags/fields are
- (*mandatory*) ```<Parameters>``` end its enclosing tag ```</Parameters>``` surround all other data.
- (*mandatory*) ```<Directories>```
  - ```Static``` (type ```std::string```) is the absolute path to the directory where the library can find the **static** XML files.
  - ```Dynamic``` (type ```std::string```) is the absolute path to the directory where the library can find the **dynamic** XML files.
- (*mandatory*) ```<Times>```
  - ```TimeStep``` (type ```double```) is the total time of the simulation.
  - ```TimeStepMechanical``` (type ```double```) is the (smaller) time interval of the calculation of mechanical contacts.

Note that when calling the library, an absolute path to the Parameters file should be given, whereas the other string should just contain the file names since the directories in which they have been put are given by the Parameters file.

### Materials
```xml
<?xml version="1.0" encoding="utf-8"?>
<Materials>
    <Intrinsic>
        <Material Id="0" Name="asphalt" YoungModulus="1000000.0" ShearModulus="0.3"/>
        <Material Id="1" Name="stone" YoungModulus="1000000.0" ShearModulus="0.3"/>
        <Material Id="2" Name="iron" YoungModulus="1000000.0" ShearModulus="0.3"/>
        <Material Id="3" Name="wood" YoungModulus="1000000.0" ShearModulus="0.3"/>
        <Material Id="4" Name="human" YoungModulus="1000000.0" ShearModulus="0.3"/>
    </Intrinsic>
    <Binary>
        <Contact Id1="0" Id2="1" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="0" Id2="2" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="0" Id2="3" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="0" Id2="4" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="1" Id2="2" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="1" Id2="3" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="1" Id2="4" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="2" Id2="3" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="2" Id2="4" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
        <Contact Id1="3" Id2="4" GammaNormal="1.300e+04" GammaTangential="1.300e+04" KineticFriction="0.50000"/>
    </Binary>
</Materials>
```
- (*mandatory*) ```<Materials>``` and its closing tag ```</Materials>``` enclose all data.
- (*mandatory*) ```<Intrinsic>``` and its closing tag ```</Intrinsic>``` enclose the intrinsic properties of the materials:
  - (*mandatory*) One ```<Material>``` tag per material, with the fields
    - (*mandatory*, *unique*) ```Id``` (type ```std::string```) is an identifier for the material;
    - (*optional*) ```Name``` is not used byt the library;
    - (*mandatory*) ```YoungModulus``` (type ```double```) is the value of Young's modulus {math}`E`;
    - (*mandatory*) ```ShearModulus``` (type ```double```) is the value of the shear modulus {math}`G`.
- (*mandatory*) ```<Binary>``` and its closing tag ```</Binary>``` enclose the binary properties of the materials, ie the physical quantities related to the contact of two materials:
  - (*mandatory*) One ```<Contact>``` tag per couple. <span style="color: red">All couples should be given</span>. The following fields are expected:
    - (*mandatory*) ```Id1``` and ```Id2``` (type ```std::string```) is and identifier for the material;
    - (*mandatory*) ```GammaNormal``` is the value of the normal damping factor {math}`\Gamma_{\rm n}` ;
    - (*mandatory*) ```GammaTangential``` is the value of the tangential damping factor {math}`\Gamma_{\rm t}` ;
    - (*mandatory*) ```KineticFriction``` is the value of the kinetic friction coefficient {math}`\mu_{\rm dyn}`.

### Geometry
The Geometry file gives the dimensions of the area in which the simulation takes place, as well as information about obstacles.
The latter as given as **Walls**, which are an ordered list of **Corners**. Each **Corner** is linked to its direct together by a line segment, forming a wall face. Here below an example:
<figure>
    <img src="./Geometry.png"
         alt="An example of Geometry">
</figure>

```xml
<?xml version="1.0" encoding="utf-8"?>
<Geometry>
    <Dimensions Lx="11.57" Ly="4.7"/>
    <Wall MaterialId="1">
        <Corner Coordinates="0.0,0.0"/>
        <Corner Coordinates="0.0,4.7"/>
        <Corner Coordinates="11.57,4.7"/>
        <Corner Coordinates="11.57,0.0"/>
        <Corner Coordinates="0.0,0.0"/>
    </Wall>
    <Wall MaterialId="3">
        <Corner Coordinates="5.0,2.15"/>
        <Corner Coordinates="6.0,2.65"/>
        <Corner Coordinates="5.0,2.95"/>
        <Corner Coordinates="5.5,2.65"/>
        <Corner Coordinates="5.0,2.15"/>
    </Wall>
</Geometry>
```
- (*mandatory*) ```<Geometry>``` and its closing tag ```</Geometry>``` enclose all data.
  - (*mandatory*) ```<Dimensions>``` contain the dimensions of the rectangular domain:
    - (*mandatory*) ```Lx``` (type ```double```) is the length of the domain along the x-axis;
    - (*mandatory*) ```Ly``` (type ```double```) is the length of the domain along the y-axis.
  - (*mandatory*) One ```<Wall>``` tag per wall, with the field
    - (*optional*) ```MaterialId``` (type ```std::string```) related to the Ids in the [Materials file](#Materials). If not given or not found, the default value for walls is used.
    - (*mandatory*) ```Corner``` tags: at least two of them must be present. Each one contains the *mandatory* field ```Coordinates``` (type ```std::pair<double>```).
  - (*mandatory*) A closing ```</Wall>``` tag after the list of corners.

Note that in the example, the first wall is actually enclosing the whole domain and thus acts as a strict boundary.

### Agents
```xml
<?xml version="1.0" encoding="utf-8"?>
<Agents>
    <Agent Type="pedestrian" Id="0" Mass="86.18248" MomentOfInertia="1.8012803784713227" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.09067151245046144" MaterialId="4" Position="-0.016965978638317853,0.16021913700431287"/>
        <Shape Id="1" Type="disk" Radius="0.12468793467309253" MaterialId="4" Position="0.009540179910355141,0.07030548198489682"/>
        <Shape Id="2" Type="disk" Radius="0.1303428066320288" MaterialId="4" Position="0.014851597455925514,-4.08006961549745e-17"/>
        <Shape Id="3" Type="disk" Radius="0.12468793467309265" MaterialId="4" Position="0.009540179910355133,-0.0703054819848968"/>
        <Shape Id="4" Type="disk" Radius="0.09067151245046151" MaterialId="4" Position="-0.016965978638317905,-0.1602191370043128"/>
    </Agent>
    <Agent Type="pedestrian" Id="1" Mass="56.699" MomentOfInertia="0.9530544567910229" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.07121708834731487" MaterialId="4" Position="-0.016965978638317752,0.15769702291032459"/>
        <Shape Id="1" Type="disk" Radius="0.09793496787989943" MaterialId="4" Position="0.00954017991035527,0.06919875746799978"/>
        <Shape Id="2" Type="disk" Radius="0.10237653397942074" MaterialId="4" Position="0.014851597455925177,2.1038726316646717e-16"/>
        <Shape Id="3" Type="disk" Radius="0.09793496787989944" MaterialId="4" Position="0.009540179910355131,-0.06919875746799974"/>
        <Shape Id="4" Type="disk" Radius="0.07121708834731486" MaterialId="4" Position="-0.016965978638317808,-0.1576970229103248"/>
    </Agent>
    <Agent Type="pedestrian" Id="2" Mass="108.86207999999999" MomentOfInertia="2.841391222285689" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.1042201294246675" MaterialId="4" Position="-0.016965978638318006,0.17565418070371278"/>
        <Shape Id="1" Type="disk" Radius="0.14331946537700047" MaterialId="4" Position="0.009540179910355093,0.07707850677478216"/>
        <Shape Id="2" Type="disk" Radius="0.1498193182140448" MaterialId="4" Position="0.014851597455925347,8.534839501805891e-18"/>
        <Shape Id="3" Type="disk" Radius="0.14331946537700024" MaterialId="4" Position="0.009540179910355195,-0.07707850677478216"/>
        <Shape Id="4" Type="disk" Radius="0.10422012942466749" MaterialId="4" Position="-0.01696597863831799,-0.17565418070371272"/>
    </Agent>
    <Agent Type="pedestrian" Id="3" Mass="56.699" MomentOfInertia="0.8577106761230354" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.07920729808468932" MaterialId="4" Position="-0.016965978638317877,0.13119717737661835"/>
        <Shape Id="1" Type="disk" Radius="0.10892279330414581" MaterialId="4" Position="0.00954017991035508,0.05757040615112575"/>
        <Shape Id="2" Type="disk" Radius="0.11386268144295812" MaterialId="4" Position="0.014851597455925339,-3.691491556878646e-17"/>
        <Shape Id="3" Type="disk" Radius="0.10892279330414578" MaterialId="4" Position="0.009540179910355254,-0.05757040615112579"/>
        <Shape Id="4" Type="disk" Radius="0.0792072980846892" MaterialId="4" Position="-0.016965978638317905,-0.1311971773766183"/>
    </Agent>
    <Agent Type="pedestrian" Id="4" Mass="54.431039999999996" MomentOfInertia="0.8358544321916865" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.07851249742150194" MaterialId="4" Position="-0.01696597863831797,0.13439281558771488"/>
        <Shape Id="1" Type="disk" Radius="0.10796733047617478" MaterialId="4" Position="0.00954017991035518,0.05897267861920459"/>
        <Shape Id="2" Type="disk" Radius="0.11286388627519121" MaterialId="4" Position="0.014851597455925512,-3.9968028886505634e-17"/>
        <Shape Id="3" Type="disk" Radius="0.10796733047617481" MaterialId="4" Position="0.009540179910355256,-0.05897267861920454"/>
        <Shape Id="4" Type="disk" Radius="0.07851249742150193" MaterialId="4" Position="-0.01696597863831796,-0.1343928155877149"/>
    </Agent>
    <Agent Type="pedestrian" Id="5" Mass="90.7184" MomentOfInertia="2.0128438381219813" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.0990091228159563" MaterialId="4" Position="-0.016965978638317888,0.15637147151866795"/>
        <Shape Id="1" Type="disk" Radius="0.13615349191909604" MaterialId="4" Position="0.009540179910355509,0.0686170945578841"/>
        <Shape Id="2" Type="disk" Radius="0.14232835210571448" MaterialId="4" Position="0.014851597455925363,-1.6653345369377347e-17"/>
        <Shape Id="3" Type="disk" Radius="0.13615349191909606" MaterialId="4" Position="0.009540179910354931,-0.06861709455788402"/>
        <Shape Id="4" Type="disk" Radius="0.09900912281595613" MaterialId="4" Position="-0.01696597863831782,-0.1563714715186678"/>
    </Agent>
    <Agent Type="pedestrian" Id="6" Mass="92.98636" MomentOfInertia="2.0706312801914812" FloorDamping="2.0" AngularDamping="5.0">
        <Shape Id="0" Type="disk" Radius="0.09345071606342613" MaterialId="4" Position="-0.01696597863831782,0.16593658168559297"/>
        <Shape Id="1" Type="disk" Radius="0.12850978730542723" MaterialId="4" Position="0.00954017991035518,0.07281434398200365"/>
        <Shape Id="2" Type="disk" Radius="0.13433798868343216" MaterialId="4" Position="0.014851597455925425,-5.218048215738236e-17"/>
        <Shape Id="3" Type="disk" Radius="0.12850978730542714" MaterialId="4" Position="0.009540179910355105,-0.07281434398200376"/>
        <Shape Id="4" Type="disk" Radius="0.09345071606342621" MaterialId="4" Position="-0.01696597863831787,-0.16593658168559286"/>
    </Agent>
</Agents>
```

- (*mandatory*) ```<Agents>``` and its closing tag ```</Agents>``` enclose all data.
  - (*mandatory*) ```<Agent>``` and its closing tag ```</Agent>``` enclose each agent. It contains the following fields:
    - (*optional*, *unused*) ```Type``` is unused for now since the current version only handles pedestrians, but we mention it since we are working on adapting the model to other active modes.
    - (*mandatory*, *unique*) ```Id``` (type ```std::string```) is a unique Id for the agent;
    - (*mandatory*) ```Mass``` (type ```double```) is the mass (in {math}`\rm kg`) of the agent;
    - (*mandatory*) ```MomentOfInertia``` (type ```double```) is the moment of inertia (in {math}`\rm kg\,m^2`) of the agent, with respect to a vertical axis going through the center of mass of the agent;
    - (*optional*) ```FloorDamping``` is the inverse of the quantity {math}`\tau_{\rm mech}` (in {math}`\rm s^{-1}`) found in the equations of motion of an unhindered agent. If not given, the default value is used;
    - (*optional*) ```AngularDamping``` is the angular version (ie related to angular movement) of the above. If not given, the default value is used;
  - (*mandatory*) Each ```<Agent>``` encloses exactly **five** ```<Shape>``` tags, which <span style="color:red">should be given in a specific order</span>, ie from the left shoulder to the right shoulder. They consisting in the following fields:
    - (*mandatory*, *unique within a specific agent*) ```Id``` (type ```std::string```) is an identifier for the shape.
    - (*optional*, *unused*) ```Type``` is unused for now since the current version only handles disks, but we mention it since we are working on adapting the model to other active modes.
    - (*mandatory*) ```Radius``` (type ```double```) is the radius of the disk;
    - (*optional*) ```MaterialId``` (type ```std::string```) related to the Ids in the [Materials file](#Materials). If not given or not found, the default value for humans is used.
    - (*mandatory*) ```Position``` (type ```std::pair<double>```) is the position of the center of mass of the shape, <span style="color: red">relative to the center of mass of the agent</span>.

## Dynamic information
### Agent Dynamics
#### As input
```xml
<?xml version="1.0" encoding="utf-8"?>
<Agents>
    <Agent Id="0">
        <Kinematics Position="-0.3238412322203901,0.259771701823956" Velocity="0.0,0.0" Theta="-0.066937014534676" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="1">
        <Kinematics Position="-0.4196349241832557,-0.60110130122263598" Velocity="0.0,0.0" Theta="-1.921604453854156" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="2">
        <Kinematics Position="0.5535867845797549,0.05479066198570259" Velocity="0.0,0.0" Theta="0.040357044672756144" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="3">
        <Kinematics Position="0.5509433024348762,-0.5054351424434713" Velocity="0.0,0.0" Theta="0.08475135886610266" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="4">
        <Kinematics Position="-0.017292568706642242,-0.5950742365642409" Velocity="0.0,0.0" Theta="-0.7694589274884652" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="5">
        <Kinematics Position="0.4133925313777592,0.5507301162474092" Velocity="0.0,0.0" Theta="0.7290673029090031" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
    <Agent Id="6">
        <Kinematics Position="-0.034584742853356644,0.47093271500912293" Velocity="0.0,0.0" Theta="0.5070191866356232" Omega="0.0"/>
        <Dynamics Fp="1000.0,1000.0" Mp="0.0"/>
    </Agent>
</Agents>
```
- (*mandatory*) ```<Agents>``` and its closing tag ```</Agents>``` enclose all data.
  - (*mandatory*) ```<Agent>``` and its closing tag ```</Agent>``` enclose each agent. It contains the ```Id``` of the agent, which should be in the [Agents file](#agents):
    - (*mandatory*) The ```<Kinematics>``` tag is the current state of the agent, and contains the following fields:
      - (*mandatory*) ```Position``` (type ```std::pair<double>```) is the position of the center of mass of the agent;
      - (*mandatory*) ```Velocity``` (type ```std::pair<double>```) is the velocity of the center of mass of the agent;
      - (*mandatory*) ```Theta``` (type ```double```) is the angle between the direction of the body, ie the line of sight when looking straight, and the x-axis.
      - (*mandatory*) ```Omega``` (type ```double```) is the angular speed of the body.
    - (*mandatory*) The ```<Dynamics>``` tag is the driving forces given to the agent, and contains the following fields:
      - (*mandatory*) ```Fp``` (type ```std::pair<double>```) is the driving force;
      - (*mandatory*) ```Mp``` (type ```double```) is the driving torque;

> Note: All angular quantities are given with the right-handed convention, ie a positive value is to be taken counterclockwise.
>
> Note2: The driving force and torque are related to the equations of motion of the unhindered agent, ie
```{math}
\frac{{\rm d}{\bf v}}{{\rm d}t}=\frac{{\bf v}^{\rm des}-{\bf v}}{\tau_{\rm mech}}\;,
```
> by {math}`{\bf F}_{\rm p}=m\frac{{\bf v}^{\rm des}}{\tau_{\rm mech}}.` Same goes for the angular version.

#### As output
The output of ```CrowdMechanics``` will have the same structure, except that the ```Dynamics``` tag will no longer be present. The ```Kinematics``` tag will contain the new state of the agent, after a time ```TimeStep```, eg:
```xml
<?xml version="1.0" encoding="utf-8"?>
<Agents>
    <Agent Id="0">
        <Kinematics Position="-0.269507,0.314106" Velocity="1.05166,1.05166" Theta="-0.066937" Omega="0"/>
    </Agent>
    <Agent Id="1">
        <Kinematics Position="-0.352324,-0.515387" Velocity="1.37579,1.38508" Theta="-1.92214" Omega="-0.110773"/>
    </Agent>
    <Agent Id="2">
        <Kinematics Position="0.585494,0.0468851" Velocity="-0.00640525,0.0626351" Theta="0.0404432" Omega="-0.100961"/>
    </Agent>
    <Agent Id="3">
        <Kinematics Position="0.621465,-0.441009" Velocity="-0.0029103,0.0656684" Theta="0.0886958" Omega="0.239468"/>
    </Agent>
    <Agent Id="4">
        <Kinematics Position="0.012522,-0.597122" Velocity="0.250815,0.0201641" Theta="-0.882874" Omega="-0.991497"/>
    </Agent>
    <Agent Id="5">
        <Kinematics Position="0.442605,0.548886" Velocity="0.0826052,0.0454557" Theta="0.755286" Omega="0.407788"/>
    </Agent>
    <Agent Id="6">
        <Kinematics Position="0.0150781,0.519899" Velocity="0.498381,0.0220522" Theta="0.507439" Omega="0.286958"/>
    </Agent>
</Agents>
```

### Agent Interactions
The library outputs information about collisions between agents, and between agents and walls. This serves two purposes:
- The total normal force on the agents allows computation of the pressure exerted on them;
- If the current execution of the library is a part of a series of consecutive runs in time, this file should remain as is since it will be used by the next execution to gather technical information about current existing contacts.

Since this file should not be "prepared" by the user, it will always have the same name ```AgentInteractions.xml``` and will always be stored in the current working directory.

```xml
<?xml version="1.0" encoding="utf-8"?>
<Interactions>
    <Agent Id="1">
        <Agent Id="4">
            <Interaction ParentShape="0" ChildShape="4" TangentialRelativeDisplacement="0.0702898,0.116009" Fn="24.0482,-24.2272" Ft="-12.1136,-12.0241" />
        </Agent>
    </Agent>
    <Agent Id="2">
        <Agent Id="5">
            <Interaction ParentShape="0" ChildShape="4" TangentialRelativeDisplacement="-0.00856562,-0.00110708" Fn="1.87401,-15.7522" Ft="7.87609,0.937003" />
        </Agent>
        <Agent Id="3">
            <Interaction ParentShape="4" ChildShape="0" TangentialRelativeDisplacement="-0.014449,-0.00107084" Fn="-1.03866,10.9581" Ft="-5.47907,-0.519329" />
        </Agent>
        <Wall ShapeId="2" WallId="0" CornerId="1" TangentialRelativeDisplacement="5.56437e-20,0.00187981" Ft="-5.87726e-15,-10.4114" Fn="-20.8227,1.15847e-14" />
    </Agent>
    <Agent Id="3">
        <Wall ShapeId="2" WallId="0" CornerId="1" TangentialRelativeDisplacement="2.21771e-20,0.000800011" Ft="-0,-20.4459" Fn="-40.8918,0" />
    </Agent>
    <Agent Id="4">
        <Wall ShapeId="3" WallId="0" CornerId="0" TangentialRelativeDisplacement="0.00114503,2.68642e-19" Ft="-17.0155,-2.49639e-14" Fn="4.92101e-14,-34.031" />
        <Wall ShapeId="4" WallId="0" CornerId="0" TangentialRelativeDisplacement="0.0234234,5.68356e-19" Ft="-285.367,-0" Fn="2.01765e-13,-570.733" />
    </Agent>
    <Agent Id="5">
        <Wall ShapeId="0" WallId="0" CornerId="2" TangentialRelativeDisplacement="0.0478101,-4.8409e-19" Ft="-17.6357,-0" Fn="0,-35.2714" />
    </Agent>
    <Agent Id="6">
        <Wall ShapeId="0" WallId="0" CornerId="2" TangentialRelativeDisplacement="0.00153013,-4.37696e-20" Ft="-10.2514,4.56527e-15" Fn="-9.14726e-15,-20.5028" />
    </Agent>
</Interactions>
```
> **<span style="color: red">Important note</span>** The files give only one of the reciprocal interactions between two agents: it will only give the couples {math}`i,j` with {math}`i < j`.

- (*mandatory*) ```<Interactions>``` and its closing tag ```</Interactions>``` enclose all data.
  - (*mandatory*) ```<Agent>``` and its closing tag ```</Agent>``` enclose each agent. It contains the ```Id``` of the agent, which should be in the [Agents file](#agents). It corresponds to the index {math}`i` in the note above and will be name the "Parent".
    - (*optional*) ```<Agent>``` and its closing tag ```</Agent>``` enclose each "Child" agent. It contains the ```Id``` of the agent, which should be in the [Agents file](#agents), and corresponds to the index {math}`j` above.
      - (*mandatory*) For each couple, we can have several ```<Interaction>``` tags, as multiple shapes could touch each other. The tag contains the following:
        - (*mandatory*) ```ParentShape``` refers to the ```Id``` of the shape of the Parent that is in touch with the Child, and that comes from the [Agents file](#agents);
        - (*mandatory*) ```ChildShape``` refers to the ```Id``` of the shape of the Child that is in touch with ```ParentShape```, and that comes from the [Agents file](#agents);
        - (*mandatory*) ```TangentialRelativeDisplacement``` (type ```std::pair<double>```) is a technical field used by the library to know if there is a contact, that represents the relative displacement that has occurred during the contact;
        - (*mandatory*) ```Fn``` (type ```std::pair<double>```) is the normal force exerted on the ```ParentShape```, as a result of its contact with ```ChildShape```;
        - (*mandatory*) ```Ft``` (type ```std::pair<double>```) is the tangential force exerted on the ```ParentShape```, as a result of its contact with ```ChildShape```.
    - (*optional*) There will be a ```<Wall>``` tag for each contact between the Parent and a wall face:
      - (*mandatory*) ```ShapeId``` is the Id of the shape of the Parent that is in contact with a wall;
      - (*mandatory*) ```WallId``` (type ```unsigned```) is a number attributed to the ```<Wall>``` tags coming from the [Geometry file](#geometry);
      - (*mandatory*) ```CornerId``` (type ```unsigned```) is a number attributed to the ```<Corner>``` tags coming from the [Geometry file](#geometry). In this context, it represents the wall face joining corner ```CornerId``` to corner ```CornerId + 1``` ;
      - (*mandatory*) The same 3 fields as for the agent/agent interactions complete the ```<Wall>``` tag.
