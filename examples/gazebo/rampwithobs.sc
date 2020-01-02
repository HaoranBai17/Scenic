# from scenic.simulators.gazebo.gazebo_models import *

# ego = Sun at 6 @ -3

# buildFrame()
# buildMaze(4, -1, 4)



# ego = Sun at 6 @ 3
# cone = Cone at 1 @ 1
# wheel = Car_wheel at 0 @ 0, facing toward 2 @ 2

from scenic.simulators.gazebo.gazebo_models import Sun, Ramp, FlatSurface
ego = Sun at 6 @ 3
start_point = 0 @ 1
ramp0 = Ramp at start_point
ramp1 = Ramp left of start_point by 0.6
flat1 = FlatSurface ahead of ramp0.position by 1.1
flat2 = FlatSurface ahead of ramp1.position by 1.1
