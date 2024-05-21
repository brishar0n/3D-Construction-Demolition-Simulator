from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, DirectionalLight, AmbientLight, GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomTriangles, GeomVertexWriter, BitMask32

from buildingMaterials import wood, metal, bricks
from destructionMethods import wrecking_ball, explosive

import random

class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.setup_camera()
        self.setup_lighting()
        self.setup_controls()
        
        self.current_material = None
        self.current_destruction_method = None
        self.destruction_location = None
        
        self.build_structure()
    
    def setup_camera(self):
        self.disableMouse()
        self.camera.setPos(0, -15, 5)
        self.camera.lookAt(0, 0, 0)
    
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
    
    def setup_controls(self):
        self.accept("arrow_up", self.move_cube, [Vec3(0, 1, 0)])
        self.accept("arrow_down", self.move_cube, [Vec3(0, -1, 0)])
        self.accept("arrow_left", self.move_cube, [Vec3(-1, 0, 0)])
        self.accept("arrow_right", self.move_cube, [Vec3(1, 0, 0)])
        self.accept("m", self.select_material, [wood])
        self.accept("n", self.select_material, [metal])
        self.accept("b", self.select_material, [bricks])
        self.accept("w", self.select_destruction_method, [wrecking_ball])
        self.accept("e", self.select_destruction_method, [explosive])
        self.accept("mouse1", self.select_destruction_location)
        
        self.move_speed = 0.1
    
    def select_material(self, material):
        self.current_material = material
    
    def select_destruction_method(self, method):
        self.current_destruction_method = method
    
    def select_destruction_location(self):
        self.destruction_location = self.camera.getPos(render)    
        self.destroy_structure()
    
    def build_structure(self):
        if self.current_material:
            print("Building structure with", self.current_material.name)
            # Generate building structure based on user-selected material
            format = GeomVertexFormat.getV3n3()
            vdata = GeomVertexData("building", format, Geom.UHStatic)
            vertex_writer = GeomVertexWriter(vdata, "vertex")
            normal_writer = GeomVertexWriter(vdata, "normal")
            
            # Generate random building structure
            for _ in range(20):
                x = random.uniform(-5, 5)
                y = random.uniform(-5, 5)
                z = random.uniform(0, 10)
                
                vertex_writer.addData3f(x, y, z)
                normal_writer.addData3f(0, 0, 1)
            
            tris = GeomTriangles(Geom.UHStatic)
            for i in range(0, len(vdata), 4):
                tris.addVertices(i, i + 1, i + 2)
                tris.addVertices(i + 2, i + 3, i)
            
            geom = Geom(vdata)
            geom.addPrimitive(tris)
            
            building_node = GeomNode("building_node")
            building_node.addGeom(geom)
            
            building_np = self.render.attachNewNode(building_node)
            building_np.setPos(0, 0, 0)
            building_np.setCollideMask(BitMask32.bit(1))
    
    def destroy_structure(self):
        if self.current_destruction_method and self.destruction_location:
            print("Destroying structure with", self.current_destruction_method.name, "at", self.destruction_location)
            # Simulate destruction using physics
            if self.current_destruction_method == wrecking_ball:
                print("Using wrecking ball with force:", self.current_destruction_method.force)
                # Apply force to objects
            elif self.current_destruction_method == explosive:
                print("Using explosive with force:", self.current_destruction_method.force)
                # Apply force to objects
    
    def move_cube(self, direction):
        # Move cube (if applicable)
        pass

app = Main()
app.run()