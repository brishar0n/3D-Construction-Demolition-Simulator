from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, DirectionalLight, AmbientLight, WindowProperties, CollisionNode, CollisionTraverser, CollisionRay, CollisionHandlerQueue, GeomNode, CardMaker
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletBoxShape, BulletDebugNode
from direct.gui.DirectGui import DirectSlider, DirectFrame, OnscreenText, DirectButton

# CONSTANTS

MOUSE_SENSITIVITY = 2
CAMERA_SPEED = 5

# MAIN

class main(ShowBase):
    physics_world = BulletWorld()
    alt_pressed = False
    current_block_size = 1.0
    
    def __init__(self):
        ShowBase.__init__(self)

        self.camera_position = self.camera.getPos()

        self.setup_window()
        self.setup_camera()
        self.setup_physics()
        self.setup_lighting()
        self.add_plane()
        self.add_cube(Vec3(0, 0, 1))
        self.setup_controls()

        self.taskMgr.add(self.update, "update")

        self.moving_forward = False
        self.moving_backward = False
        self.moving_left = False
        self.moving_right = False

        self.mouse_watcher = self.mouseWatcherNode
        self.win_properties = WindowProperties()
        self.win_properties.setCursorHidden(True)
        self.win.requestProperties(self.win_properties)

        self.camera_heading = 0
        self.camera_pitch = 0

        self.picker_ray = CollisionRay()
        self.picker_ray_node = CollisionNode('mouseRay')
        self.picker_ray_node.addSolid(self.picker_ray)
        self.picker_ray_node.setFromCollideMask(GeomNode.getDefaultCollideMask())
        self.picker_ray_np = self.camera.attachNewNode(self.picker_ray_node)
        self.picker_handler = CollisionHandlerQueue()
        self.picker_traverser = CollisionTraverser('mousePicker')
        self.picker_traverser.addCollider(self.picker_ray_np, self.picker_handler)

        self.setup_ui()
        
        self.current_block_size = 1.0
    
        self.alt_pressed = False
        self.accept('alt', self.toggle_mouse)
        self.accept('mouse1', self.add_block_at_click)

    def setup_window(self):
        props = WindowProperties()
        props.setFullscreen(True)
        self.win.requestProperties(props)

    def setup_camera(self):
        self.disableMouse()
        self.camera.setPos(0, -15, 5)
        self.camera.lookAt(0, 0, 0)

    def setup_physics(self):
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))
        self.debug_node = BulletDebugNode('Debug')
        self.debug_node.showWireframe(True)
        self.debug_node.showConstraints(True)
        self.debug_np = self.render.attachNewNode(self.debug_node)
        self.physics_world.setDebugNode(self.debug_np.node())

    def setup_lighting(self):
        d_light = DirectionalLight("d_light")
        d_light.setColor((1, 1, 1, 1))
        d_light_np = self.render.attachNewNode(d_light)
        d_light_np.setHpr(0, -60, 0)
        self.render.setLight(d_light_np)

        a_light = AmbientLight("a_light")
        a_light.setColor((0.2, 0.2, 0.2, 1))
        a_light_np = self.render.attachNewNode(a_light)
        self.render.setLight(a_light_np)

    def add_plane(self):
        plane_shape = BulletBoxShape(Vec3(10, 10, 0.1))
        plane_node = BulletRigidBodyNode('Ground')
        plane_node.addShape(plane_shape)
        plane_node.setMass(0)
        plane_np = self.render.attachNewNode(plane_node)
        plane_np.setPos(0, 0, -0.1)
        self.physics_world.attachRigidBody(plane_node)

        cm = CardMaker("ground")
        cm.setFrame(-10, 10, -10, 10)
        plane_visual = self.render.attachNewNode(cm.generate())
        plane_visual.setPos(0, 0, -0.1)
        plane_visual.lookAt(0, 0, -1)
        plane_visual.setColor(0, 1, 0.3, 1)

    def add_cube(self, position):
        size = self.current_block_size
        cube_shape = BulletBoxShape(Vec3(size * 0.5, size * 0.5, size * 0.5))
        cube_node = BulletRigidBodyNode('Box')
        cube_node.setMass(1.0)
        cube_node.addShape(cube_shape)
        cube_np = self.render.attachNewNode(cube_node)
        cube_np.setPos(position)
        self.physics_world.attachRigidBody(cube_node)

        model = self.loader.loadModel('models/box')
        model.setScale(size)
        model.reparentTo(cube_np)

    def setup_controls(self):
        self.accept("w", self.set_moving, ["forward", True])
        self.accept("w-up", self.set_moving, ["forward", False])
        self.accept("s", self.set_moving, ["backward", True])
        self.accept("s-up", self.set_moving, ["backward", False])
        self.accept("a", self.set_moving, ["left", True])
        self.accept("a-up", self.set_moving, ["left", False])
        self.accept("d", self.set_moving, ["right", True])
        self.accept("d-up", self.set_moving, ["right", False])
        self.accept("escape", self.exit_app)

        self.move_speed = CAMERA_SPEED
        self.mouse_sensitivity = MOUSE_SENSITIVITY

    def set_moving(self, direction, value):
        if direction == "forward":
            self.moving_forward = value
        elif direction == "backward":
            self.moving_backward = value
        elif direction == "left":
            self.moving_left = value
        elif direction == "right":
            self.moving_right = value

    def setup_ui(self):
        self.ui_frame = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                    frameSize=(-1.3, 1.3, -0.1, 0.1),
                                    pos=(0, 0, -0.95))

        self.block_size_label = OnscreenText(text="Block Size:",
                                             pos=(-1.1, -0.03),
                                             scale=0.05,
                                             parent=self.ui_frame)

        self.block_size_slider = DirectSlider(range=(0.5, 3.0),
                                              value=self.current_block_size,
                                              pageSize=0.1,
                                              command=self.set_block_size,
                                              scale=0.3,
                                              pos=(-0.3, 0, -0.03),
                                              parent=self.ui_frame)
        
        self.toggle_button = DirectButton(text="Toggle Mouse",
                                          scale=0.05,
                                          command=self.toggle_mouse,
                                          pos=(0.5, 0, -0.03),
                                          parent=self.ui_frame)

    def set_block_size(self):
        self.current_block_size = self.block_size_slider['value']

    def toggle_mouse(self):
        self.alt_pressed = not self.alt_pressed

        if self.alt_pressed:
            self.win_properties.setCursorHidden(False)
            self.win.movePointer(0, int(self.win.getProperties().getXSize() / 2), int(self.win.getProperties().getYSize() / 2))
            self.disable_controls()
        else:
            self.disableMouse()
            self.win_properties.setCursorHidden(True)
            self.win.movePointer(0, int(self.win.getProperties().getXSize() / 2), int(self.win.getProperties().getYSize() / 2))
            self.enable_controls()

        self.win.requestProperties(self.win_properties)

    def disable_controls(self):
        self.ignore("w")
        self.ignore("w-up")
        self.ignore("s")
        self.ignore("s-up")
        self.ignore("a")
        self.ignore("a-up")
        self.ignore("d")
        self.ignore("d-up")

    def enable_controls(self):
        self.accept("w", self.set_moving, ["forward", True])
        self.accept("w-up", self.set_moving, ["forward", False])
        self.accept("s", self.set_moving, ["backward", True])
        self.accept("s-up", self.set_moving, ["backward", False])
        self.accept("a", self.set_moving, ["left", True])
        self.accept("a-up", self.set_moving, ["left", False])
        self.accept("d", self.set_moving, ["right", True])
        self.accept("d-up", self.set_moving, ["right", False])

    def exit_app(self):
        self.userExit()

    def add_block_at_click(self):
        if self.mouse_watcher.hasMouse():
            mpos = self.mouse_watcher.getMouse()
            self.picker_ray.setFromLens(self.camNode, mpos.getX(), mpos.getY())
            self.picker_traverser.traverse(self.render)
            if self.picker_handler.getNumEntries() > 0:
                self.picker_handler.sortEntries()
                entry = self.picker_handler.getEntry(0)
                point = entry.getSurfacePoint(self.render)
                point.setZ(point.getZ() + self.current_block_size * 2)
                self.add_cube(point)

    def update(self, task):
        dt = globalClock.getDt()
        self.physics_world.doPhysics(dt)

        if self.moving_forward:
            self.camera.setY(self.camera, self.move_speed * dt)
        if self.moving_backward:
            self.camera.setY(self.camera, -self.move_speed * dt)
        if self.moving_left:
            self.camera.setX(self.camera, -self.move_speed * dt)
        if self.moving_right:
            self.camera.setX(self.camera, self.move_speed * dt)

        if not self.alt_pressed:
           if self.mouse_watcher.hasMouse():
            mouse_x = self.mouse_watcher.getMouseX()
            mouse_y = self.mouse_watcher.getMouseY()
            self.camera_heading -= mouse_x * self.mouse_sensitivity
            self.camera_pitch = max(-90, min(90, self.camera_pitch + mouse_y * self.mouse_sensitivity))
            self.camera.setHpr(self.camera_heading, self.camera_pitch, 0)

           self.win.movePointer(0, int(self.win.getProperties().getXSize() / 2), int(self.win.getProperties().getYSize() / 2))

        return task.cont

app = main()
app.run()
