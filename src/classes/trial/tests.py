import numpy as np
from shapely.geometry import Point, Polygon

from struct_trial import Agent, AgentTypes, BodyMeasures, Shapes, ShapeTypes


def main():
    # Test 1: Create a pedestrian agent with three circles of different radii
    print("=== Test 1: Pedestrian Agent with Circles ===")
    pedestrian_shapes = Shapes()
    pedestrian_shapes.create_shape(name="circle1", shape_type=ShapeTypes.CIRCLE, center=(0, 0), radius=1, young_modulus=1.0)
    pedestrian_shapes.create_shape(name="circle2", shape_type=ShapeTypes.CIRCLE, center=(0, 0), radius=2, young_modulus=1.5)
    pedestrian_shapes.create_shape(name="circle3", shape_type=ShapeTypes.CIRCLE, center=(0, 0), radius=3, young_modulus=2.0)

    pedestrian_measures = BodyMeasures(
        agent_type=AgentTypes.PEDESTRIAN,
        measures={"bideltoid_breadth": 50.0, "chest_depth": 30.0, "height": 170.0},
    )

    pedestrian_agent = Agent(
        sex="male",
        agent_type=AgentTypes.PEDESTRIAN,
        measures=pedestrian_measures,
        shapes=pedestrian_shapes,
    )
    print(pedestrian_agent.shapes.shapes)
    pedestrian_agent.rotate(np.pi / 2.0)
    print(pedestrian_agent.shapes.shapes)
    exit(0)

    print("Pedestrian Agent:")
    print(f"Sex: {pedestrian_agent.sex}")
    print(f"Agent Type: {pedestrian_agent.agent_type}")
    print(f"Number of Shapes: {pedestrian_agent.shapes.number_of_shapes()}")
    for name, shape in pedestrian_agent.shapes.shapes.items():
        print(f" - {name}: {shape}")

    # Test 2: Create a robot agent made of two rectangles
    print("\n=== Test 2: Robot Agent with Rectangles ===")
    robot_shapes = Shapes()
    robot_shapes.create_shape(
        name="rectangle1",
        shape_type=ShapeTypes.RECTANGLE,
        min_x=0,
        min_y=0,
        max_x=2,
        max_y=1,
        young_modulus=2.5,
    )
    robot_shapes.create_shape(
        name="rectangle2",
        shape_type=ShapeTypes.RECTANGLE,
        min_x=2,
        min_y=0,
        max_x=4,
        max_y=1,
        young_modulus=3.0,
    )

    robot_measures = BodyMeasures(agent_type=AgentTypes.CUSTOM, measures={})  # No specific measures for custom agents

    robot_agent = Agent(
        sex=None,
        agent_type=AgentTypes.CUSTOM,
        measures=robot_measures,
        shapes=robot_shapes,
    )

    print("Robot Agent:")
    print(f"Sex: {robot_agent.sex}")
    print(f"Agent Type: {robot_agent.agent_type}")
    print(f"Number of Shapes: {robot_agent.shapes.number_of_shapes()}")
    for name, shape in robot_agent.shapes.shapes.items():
        print(f" - {name}: {shape}")

    # Test 3: Initialize agents using dictionaries
    print("\n=== Test 3: Initialize Agents Using Dictionaries ===")

    # Pedestrian agent from dictionary
    pedestrian_dict = {
        "sex": "female",
        "agent_type": AgentTypes.PEDESTRIAN,
        "measures": {"bideltoid_breadth": 45.0, "chest_depth": 28.0, "height": 160.0},
        "shapes": {
            "circle1": {"shape_type": ShapeTypes.CIRCLE, "center": (1, 1), "radius": 2.5},
            "circle2": {"shape_type": ShapeTypes.CIRCLE, "center": (2, 2), "radius": 3.5},
            "circle3": {"shape_type": ShapeTypes.CIRCLE, "center": (3, 3), "radius": 4.5},
        },
    }

    pedestrian_from_dict = Agent(
        sex=pedestrian_dict["sex"],
        agent_type=pedestrian_dict["agent_type"],
        measures=BodyMeasures(agent_type=pedestrian_dict["agent_type"], measures=pedestrian_dict["measures"]),
        shapes={
            name: {
                **shape_data,
                "object": Point(shape_data["center"]).buffer(shape_data["radius"]),
            }
            for name, shape_data in pedestrian_dict["shapes"].items()
        },
    )

    print("Pedestrian Agent from Dictionary:")
    print(f"Sex: {pedestrian_from_dict.sex}")
    print(f"Agent Type: {pedestrian_from_dict.agent_type}")
    print(f"Number of Shapes: {pedestrian_from_dict.shapes.number_of_shapes()}")

    # Robot agent from dictionary
    robot_dict = {
        "sex": None,
        "agent_type": AgentTypes.CUSTOM,
        "measures": {},
        "shapes": {
            "rectangle1": {"shape_type": ShapeTypes.RECTANGLE, "min_x": 0, "min_y": 0, "max_x": 2, "max_y": 1},
            "rectangle2": {"shape_type": ShapeTypes.RECTANGLE, "min_x": 2, "min_y": 0, "max_x": 4, "max_y": 1},
        },
    }

    robot_from_dict = Agent(
        sex=None,
        agent_type=robot_dict["agent_type"],
        measures=BodyMeasures(agent_type="custom", measures={}),
        shapes={
            name: {
                **shape_data,
                "object": Polygon(
                    [
                        (shape_data["min_x"], shape_data["min_y"]),
                        (shape_data["min_x"], shape_data["max_y"]),
                        (shape_data["max_x"], shape_data["max_y"]),
                        (shape_data["max_x"], shape_data["min_y"]),
                    ]
                ),
            }
            for name, shape_data in robot_dict["shapes"].items()
        },
    )

    print("Robot Agent from Dictionary:")
    print(f"Sex: {robot_from_dict.sex}")
    print(f"Agent Type: {robot_from_dict.agent_type}")
    print(f"Number of Shapes: {robot_from_dict.shapes.number_of_shapes()}")


if __name__ == "__main__":
    main()
