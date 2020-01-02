# all classes are derived from the Scenic 'Object' base class


constructor Box:
    model_name: 'box'
    static: 'true'
    x: self.position[0]  # isolate x coordinate of position, default value = 0
    y: self.position[1]  # isolate y coordinate of position, default value = 0
    z: 0
    roll: 0
    pitch: 0
    yaw: self.heading  # default heading = 0
    shape_type: 'box'  # SDF built-in shape type
    height: 1
    width: 1
    depth: 1
    template_name: 'box_template'
    description: 'A simple Box.'
    uri: 'model://box'

constructor Cylinder:
    model_name: 'cylinder'
    static: 'true'
    z: 0
    roll: 0
    pitch: 0
    yaw: self.heading
    shape_type: 'cylinder'
    radius: 1
    length: 1
    template_name: 'cylinder_template'
    description: 'A simple Cylinder.'
    uri: 'model://cylinder'

constructor Sphere:
    model_name: 'sphere'
    static: 'true'
    x: self.position[0]
    y: self.position[1]
    z: 0
    roll: 0
    pitch: 0
    yaw: self.heading
    shape_type: 'sphere'
    radius: 1
    template_name: 'sphere_template'
    description: 'A simple Sphere.'
    uri: 'model://sphere'

constructor Car_wheel:
    model_name: 'car_wheel'
    x: self.position[0]
    y: self.position[1]
    z: 0
    roll: 0
    pitch: 0
    yaw: self.heading
    uri: 'model://car_wheel'

constructor Beer:
    model_name: 'beer'
    x: self.position[0]
    y: self.position[1]
    z: 0
    roll: 0
    pitch: 0
    uri: 'model://beer'

constructor TurtleBot:
    model_name: 'turtlebot'
    x: self.position[0]
    y: self.position[1]
    z: 0.5
    roll: 0
    pitch: 0
    yaw: 1.5
    height: 1
    uri: 'model://turtlebot'

constructor Ramp:
    model_name: 'nist_simple_ramp_120'
    x: self.position[0]
    y: self.position[1]
    z: -0.41
    roll: -0.65
    pitch: 0
    yaw: self.heading
    uri: 'model://nist_simple_ramp_120'

constructor Ramp_down:
    model_name: 'nist_simple_ramp_120'
    x: self.position[0]
    y: self.position[1]
    z: -0.41
    roll: -0.65
    pitch: 0
    yaw: 3.15
    uri: 'model://nist_simple_ramp_120'

constructor FlatSurface(Ramp):
    roll: -0.78
    z: -0.245

constructor Sun:
    model_name: 'sun'
    x: self.position[0]
    y: self.position[1]
    z: 3.7
    roll: 0
    pitch: 0.4
    yaw: 2.5
    uri: 'model://sun'

constructor WillowGarage:
    model_name: 'willowgarage'
    x: self.position[0]
    y: self.position[1]
    z: 0
    roll: 0
    pitch: 0
    yaw: 0
    uri: 'model://willowgarage'

constructor Cone:
    model_name: 'construction_cone'
    x: self.position[0]
    y: self.position[1]
    z: 0
    roll: 0
    pitch: 0
    yaw: self.heading
    uri: 'model://construction_cone'

def buildMaze(num_wheels, Pos_low, Pos_hi):
    for x in range(0, num_wheels):
        angle1 = 5.5
        angle2 = 7
        angle_range = Uniform(angle1, angle2)
        new_angle = resample(angle_range)
        pos_range = (Pos_low, Pos_hi)
        position1 = resample(pos_range)
        position2 = resample(pos_range)
        carwheel = Car_wheel at position1 @ position2, facing new_angle

def randomConeGen(start_pos, width_gen, length_gen, num_wheels):
    start_x = start_pos[0]
    start_y = start_pos[1]
    for i in range(0, num_wheels):
        angle1 = 5.5
        angle2 = 7
        angle_range = Uniform(angle1, angle2)
        new_angle = resample(angle_range)

        positionX = (start_x, start_x + width_gen)
        positionY = (start_y, start_y + length_gen)
        cone = Cone at positionX @ positionY

def buildBoard(left_cor, right_cor, start_cor, boardLen):
     left_x = left_cor
     right_x = right_cor
     right_y = start_cor
     left_y = start_cor
     for i in range(boardLen):
         cone1 = Car_wheel at left_x @ left_y
         cone2 = Car_wheel at right_x @ right_y
         right_y = right_y + 1.000001
         left_y = left_y + 1.000001


