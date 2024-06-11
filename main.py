from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, LPoint3f, DirectionalLight, AmbientLight, WindowProperties, CollisionNode, CollisionTraverser, CollisionRay, CollisionHandlerQueue, GeomNode, CardMaker, TransparencyAttrib
from panda3d.bullet import BulletWorld, BulletRigidBodyNode, BulletBoxShape, BulletSphereShape, BulletDebugNode, BulletConeShape
from direct.gui.DirectGui import DirectSlider, DirectFrame, OnscreenText, DirectButton, DirectEntry, DirectLabel
from direct.gui.OnscreenImage import OnscreenImage

import materialManager
import destructionManager

# CONSTANTS
MOUSE_SENSITIVITY = 2
CAMERA_SPEED = 5

class MainApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.current_block_size = 1.0
        self.alt_pressed = False
        self.physics_enabled = False
        self.physics_enabled_string = 'disabled'
        self.camera_position = self.camera.getPos()
        self.selected_material = 'wood'
        self.current_shape = 'cube'
        self.placing_mode = 'building'

        self.material_manager = materialManager.MaterialManager()
        self.destruction_manager = destructionManager.DestructionManager(self)

        self.setup_window()
        self.setup_camera()
        self.setup_physics()
        self.setup_lighting()
        self.add_plane()
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
        self.debug_node.showBoundingBoxes(False)
        self.debug_np = self.render.attachNewNode(self.debug_node)

        bullet_debug_np = BulletDebugNode('BulletDebug')
        bullet_debug_np.showNormals(False)
        bullet_debug_np.showWireframe(True)
        bullet_debug_np.showConstraints(True)
        bullet_debug_np.showBoundingBoxes(False)

        self.physics_world.setDebugNode(bullet_debug_np)

        self.debug_np.setPos(0, 0, 0)
        self.debug_np.setHpr(0, 0, 0)

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
        plane_node.setFriction(1.0)
        plane_np = self.render.attachNewNode(plane_node)
        plane_np.setPos(0, 0, 0)

        self.physics_world.attachRigidBody(plane_node)

        cm = CardMaker("ground")
        cm.setFrame(-10, 10, -10, 10)
        plane_visual = self.render.attachNewNode(cm.generate())
        plane_visual.setPos(0, 0, -0.1)
        plane_visual.lookAt(0, 0, -1)
        plane_visual.setColor(0, 1, 0.3, 1)

    def add_cube(self, position):
        size = self.current_block_size

        if self.current_shape == 'cube':
            shape = BulletBoxShape(Vec3(size / 2, size / 2, size / 2))
        elif self.current_shape == 'cone':
            shape = BulletConeShape(size / 2, size)
        elif self.current_shape == 'sphere':
            shape = BulletSphereShape(size / 2)
        else:
            return

        block_node = BulletRigidBodyNode('Box')

        material_properties = self.material_manager.get_material_properties(self.selected_material, self.current_block_size)
        mass = material_properties['mass']
        friction = material_properties['friction']
        restitution = material_properties['restitution']
        color = material_properties['color']

        block_node.setMass(mass)
        block_node.addShape(shape)
        block_node.setFriction(friction)
        block_node.setRestitution(restitution)
        block_node.setLinearSleepThreshold(0.0)
        block_node.setAngularSleepThreshold(0.0)

        block_node.setCcdMotionThreshold(1e-7)
        block_node.setCcdSweptSphereRadius(0.5)

        block_node.setLinearDamping(0.1)
        block_node.setAngularDamping(0.1)

        block_np = self.render.attachNewNode(block_node)
        block_np.setPos(position)
        block_np.setName('Box')

        self.physics_world.attachRigidBody(block_node)

        if self.current_shape == 'cube':
            model = self.loader.loadModel('models/box')
        elif self.current_shape == 'cone':
            model = self.loader.loadModel('assets/Cone.egg')
        elif self.current_shape == 'sphere':
            model = self.loader.loadModel('models/misc/sphere')

        if self.current_shape == 'cone':
            model.setScale(size / 2, size / 2, size)
        else:
            model.setScale(size)
        model.setColor(color)
        model.reparentTo(block_np)

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

    def set_block_shape(self, shape):
        self.current_shape = shape
        self.update_labels()

    def setup_ui(self):
        self.ui_frame_bottom = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                           frameSize=(-1.3, 1.3, -0.1, 0.1),
                                           pos=(0, 0, -0.95))

        self.ui_frame_top = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                        frameSize=(-1.3, 1.3, -0.1, 0.1),
                                        pos=(0, 0, 0.875))

        self.ui_frame_left = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                         frameSize=(-0.3, 0.1, -0.3, 0.3),
                                         pos=(-1, 0, 0))

        self.ui_frame_right = DirectFrame(frameColor=(0, 0, 0, 0.5),
                                          frameSize=(-0.1, 0.3, -0.3, 0.3),
                                          pos=(1, 0, 0))

        self.clear_blocks_button = DirectButton(text="Clear",
                                                scale=0.05,
                                                command=self.clear_blocks,
                                                pos=(-0.1, 0, -0.1),
                                                parent=self.ui_frame_left)

        self.enable_physics_button = DirectButton(text="Toggle Physics",
                                                  scale=0.05,
                                                  command=self.enable_physics,
                                                  pos=(-0.1, 0, 0.1),
                                                  parent=self.ui_frame_left)

        self.block_size_label = OnscreenText(text="Block Size:",
                                             pos=(-1.1, -0.03),
                                             scale=0.05,
                                             parent=self.ui_frame_bottom)

        self.block_size_slider = DirectSlider(range=(0.5, 3.0),
                                              value=self.current_block_size,
                                              pageSize=0.1,
                                              command=self.set_block_size,
                                              scale=0.3,
                                              pos=(-0.3, 0, -0.03),
                                              parent=self.ui_frame_bottom)

        self.material_label = OnscreenText(text="Select Material:",
                                           pos=(-1.1, 0.03),
                                           scale=0.05,
                                           parent=self.ui_frame_top)

        self.wood_button = DirectButton(image='assets/Wood.png',
                                        scale=0.075,
                                        command=self.set_material,
                                        extraArgs=["wood"],
                                        pos=(-0.5, 0, 0),
                                        parent=self.ui_frame_top)
        self.metal_button = DirectButton(image='assets/Metal.png',
                                         scale=0.075,
                                         command=self.set_material,
                                         extraArgs=["metal"],
                                         pos=(0.0, 0, 0),
                                         parent=self.ui_frame_top)
        self.stone_button = DirectButton(image='assets/Stone.png',
                                         scale=0.075,
                                         command=self.set_material,
                                         extraArgs=["stone"],
                                         pos=(0.5, 0, 0),
                                         parent=self.ui_frame_top)

        self.cube_button = DirectButton(image='assets/Cube.png',
                                        scale=0.075,
                                        command=self.set_block_shape,
                                        extraArgs=["cube"],
                                        pos=(0.5, 0, 0.025),
                                        parent=self.ui_frame_bottom)

        self.cone_button = DirectButton(image='assets/Cone.png',
                                        scale=0.075,
                                        command=self.set_block_shape,
                                        extraArgs=["cone"],
                                        pos=(0.75, 0, 0.025),
                                        parent=self.ui_frame_bottom)

        self.sphere_button = DirectButton(image='assets/Sphere.png',
                                        scale=0.075,
                                        command=self.set_block_shape,
                                        extraArgs=["sphere"],
                                        pos=(1, 0, 0.025),
                                        parent=self.ui_frame_bottom)

        self.wrecking_ball_button = DirectButton(image='assets/Wrecking_Ball.png',
                                                scale=0.1,
                                                command=self.destruction_manager.add_wrecking_ball,
                                                pos=(0.1, 0, 0.15),
                                                parent=self.ui_frame_right)

        self.explosion_button = DirectButton(image='assets/Explosion.png',
                                            scale=0.1,
                                            command=self.show_explosion_inputs,
                                            pos=(0.1, 0, -0.1),
                                            parent=self.ui_frame_right)
        
        self.explosion_force_label = DirectLabel(text="Force:",
                                             scale=0.05,
                                             pos=(0, 0, -0.3),
                                             parent=self.ui_frame_right,
                                             frameColor=(0, 0, 0, 0))
        
        self.explosion_force_entry = DirectEntry(text="",
                                                scale=0.05,
                                                pos=(0.15, 0, -0.3),
                                                parent=self.ui_frame_right,
                                                numLines=1,
                                                focus=0,
                                                width=3)
        self.explosion_radius_label = DirectLabel(text="Radius:",
                                                scale=0.05,
                                                pos=(0, 0, -0.4),
                                                parent=self.ui_frame_right,
                                                frameColor=(0, 0, 0, 0))
        self.explosion_radius_entry = DirectEntry(text="",
                                                scale=0.05,
                                                pos=(0.15, 0, -0.4),
                                                parent=self.ui_frame_right,
                                                numLines=1,
                                                focus=0,
                                                width=3)

        self.explosion_force_label.hide()
        self.explosion_force_entry.hide()
        self.explosion_radius_label.hide()
        self.explosion_radius_entry.hide()

        self.crosshair = OnscreenImage(image='assets/crosshair.png', pos=(0, 0, 0), scale=0.005)
        self.crosshair.setTransparency(TransparencyAttrib.MAlpha)

        self.mode_label = OnscreenText(text=f"MODE: {self.placing_mode.upper()}", pos=(-1.1, -0.8), scale=0.05)
        self.shape_label = OnscreenText(text=f"BLOCK: {self.current_shape.upper()}", pos=(-0.6, -0.8), scale=0.05)
        self.material_label = OnscreenText(text=f"MATERIAL: {self.selected_material.upper()}", pos=(-0.05, -0.8), scale=0.05)
        self.physics_label = OnscreenText(text=f"PHYSICS ENABLED: {self.physics_enabled_string.upper()}", pos=(0.6, -0.8), scale=0.05)
    

    def clear_blocks(self):
        for node in self.render.getChildren():
            if node.getName() == 'Box' or node.getName() == 'WreckingBall':
                node.removeNode()

    def show_explosion_inputs(self):
        if self.placing_mode == 'explosion':
            self.explosion_force_label.hide()
            self.explosion_force_entry.hide()
            self.explosion_radius_label.hide()
            self.explosion_radius_entry.hide()
            self.placing_mode = 'building'
        else:
            self.explosion_force_label.show()
            self.explosion_force_entry.show()
            self.explosion_radius_label.show()
            self.explosion_radius_entry.show()
            self.placing_mode = 'explosion'
        self.update_labels()

    def set_block_size(self):
        self.current_block_size = self.block_size_slider['value']

    def set_material(self, material):
        self.selected_material = material
        self.update_labels()

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
            self.picker_ray.setFromLens(self.camNode, 0, 0)
            self.picker_traverser.traverse(self.render)
            if self.picker_handler.getNumEntries() > 0:
                self.picker_handler.sortEntries()
                entry = self.picker_handler.getEntry(0)
                point = entry.getSurfacePoint(self.render)

                snapped_x = round(point.getX() / self.current_block_size) * self.current_block_size
                snapped_y = round(point.getY() / self.current_block_size) * self.current_block_size
                snapped_z = round(point.getZ() / self.current_block_size) * self.current_block_size + self.current_block_size / 2

                if self.placing_mode == 'explosion':
                    try:
                        force = float(self.explosion_force_entry.get().strip())
                    except ValueError:
                        force = 100.0
                    try:
                        radius = float(self.explosion_radius_entry.get().strip())
                    except ValueError:
                        radius = 5.0
                    self.destruction_manager.trigger_explosion(Vec3(snapped_x, snapped_y, snapped_z), force, radius)
                    self.explosion_force_label.hide()
                    self.explosion_force_entry.hide()
                    self.explosion_radius_label.hide()
                    self.explosion_radius_entry.hide()
                    self.placing_mode = 'building'
                    self.update_labels()
                else:
                    self.add_cube(Vec3(snapped_x, snapped_y, snapped_z))

    def enable_physics(self):
        self.physics_enabled = not self.physics_enabled
        if self.physics_enabled:
            self.physics_enabled_string = 'enabled'
        else:
            self.physics_enabled_string = 'disabled'
        self.update_labels()

    def update_labels(self):
        self.mode_label.setText(f"MODE: {self.placing_mode.upper()}")
        self.shape_label.setText(f"BLOCK: {self.current_shape.upper()}")
        self.material_label.setText(f"MATERIAL: {self.selected_material.upper()}")
        self.physics_label.setText(f"PHYSICS ENABLED: {self.physics_enabled_string.upper()}")

    def update(self, task):
        dt = globalClock.getDt()

        if self.physics_enabled:
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

app = MainApp()
app.run()
