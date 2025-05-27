To use this Kivy-based crowd simulation application to test our library, follow these keybindings and workflow:

## Simulation Stages
The interface operates in three sequential stages controlled by <kbd>SPACE</kbd>:
1. **Wall Creation** (Stage 1)
2. **Agent Placement** (Stage 2)
3. **Simulation** (Stage 3)

## Keybindings Reference

| Key | Functionality | Stage |
|-----|---------------|-------|
| <kbd>w</kbd> | Enter wall creation mode | All |
| <kbd>a</kbd> | Enter agent placement mode | All |
| <kbd>SPACE</kbd> | Advance to next stage | All |
| <kbd>f</kbd> | Force modification mode | Stage 2 |
| <kbd>t</kbd> | Torque modification mode | Stage 2 |
| <kbd>r</kbd> | Run simulation | Stage 3 |
| <kbd>s</kbd> | Save current configuration | All |
| <kbd>q</kbd> | Quit application | All |

## Detailed Workflow

**1. Wall Creation (Stage 1)**
- **Left-click**: Start/continue drawing walls
- **Right-click**: Finish current wall segment
- Walls snap to grid nodes automatically
- Press <kbd>SPACE</kbd> when finished

**2. Agent Placement (Stage 2)**
- **Left-click**: Place new agent
- In **Force mode** (<kbd>f</kbd>), *right-click  outside the agent*, then *drag* and *hold* to set the direction and magnitude of the agent’s propulsion force—the direction follows your drag, and the force magnitude increases the longer you hold.
- In **Torque mode** (<kbd>t</kbd>):
  - *Left-click+hold outside the agent*: Apply positive torque
  - *Right-click+hold outside the agent*: Apply negative torque
- **Left-click+hold inside the agent**: Rotate agent counter-clockwise
- **Right-click+hold inside the agent**: Rotate agent clockwise

**3. Simulation (Stage 3)**
- Press <kbd>r</kbd> to run physics simulation
- Agent dynamics update automatically
- Forces/torques persist between simulation steps

## Interface Elements
- **Right panel** shows active mode
- **Agent status panel** (at the bottom of the screen) displays:
  - Position/orientation
  - Velocity/angular velocity
  - Applied forces/torque
- **Grid lines** represent 0.1m increments
- **Color-coded arrows** show propulsion force vectors
- Agents shown with **full opacity** indicate the agent you are currently configuring.
- To save configurations, press <kbd>s</kbd> at any time. The application exports:
  - `Geometry.xml` (wall layouts)
  - `Agents.xml` (agent properties)
  - `AgentDynamics.xml` (simulation states)


