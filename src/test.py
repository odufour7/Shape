""" Test the Pedestrian class. """

import src.utils.constants as cst
import src.utils.functions as fun
from src.classes.pedestrian import Pedestrian
from src.plotting import plot
from src.tabs import anthropometry_tab

pedestrian_f = Pedestrian(chest_depth=20.0, bideltoid_breadth=40.0, height=180, sex="male")

# plot.display_shape2D(pedestrian_f)
# plot.display_body3D_orthogonal_projection(pedestrian_f)
plot.display_body3D_polygons(pedestrian_f)
# plot.display_body3D_mesh(pedestrian_f)
# pedestrian_f.draw_body3D_continuous()
# pedestrian_f.draw_orthogonal_projection_body()

# anthropometry.save_anthropometric_data()
# df = fun.load_pickle(cst.PICKLE_DIR / "ANSUREIIPublic.pkl")
# plot.display_disbtribution(df, "Bideltoid breadth [cm]")
