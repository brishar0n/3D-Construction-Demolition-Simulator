from direct.showbase.ShowBaseGlobal import globalClock
from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, Point3, DirectionalLight, AmbientLight, KeyboardButton
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom, GeomNode, GeomTriangles, GeomVertexWriter

class main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.setup_camera()

        self.setup_lighting()
        
        self.add_plane()
        
        self.add_cube()
        
        self.setup_controls()
    
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
    
    def add_plane(self):
        format = GeomVertexFormat.getV3n3()
        vdata = GeomVertexData("plane", format, Geom.UHStatic)
        vertex_writer = GeomVertexWriter(vdata, "vertex")
        normal_writer = GeomVertexWriter(vdata, "normal")
        
        vertex_writer.addData3f(-5, -5, 0)
        normal_writer.addData3f(0, 0, 1)
        
        vertex_writer.addData3f(5, -5, 0)
        normal_writer.addData3f(0, 0, 1)
        
        vertex_writer.addData3f(5, 5, 0)
        normal_writer.addData3f(0, 0, 1)
        
        vertex_writer.addData3f(-5, 5, 0)
        normal_writer.addData3f(0, 0, 1)
        
        tris = GeomTriangles(Geom.UHStatic)
        tris.addVertices(0, 1, 2)
        tris.addVertices(2, 3, 0)
        
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        plane_node = GeomNode("plane_node")
        plane_node.addGeom(geom)
        
        plane_np = self.render.attachNewNode(plane_node)
        plane_np.setPos(0, 0, 0)
    
    def add_cube(self):
        cube = self.loader.loadModel("models/box")
        cube.setScale(1)
        cube.setPos(0, 0, 1)
        cube.reparentTo(self.render)
        
        self.cube_pos = Point3(0, 0, 1)
    
    def setup_controls(self):
        self.accept("arrow_up", self.move_cube, [Vec3(0, 1, 0)])
        self.accept("arrow_down", self.move_cube, [Vec3(0, -1, 0)])
        self.accept("arrow_left", self.move_cube, [Vec3(-1, 0, 0)])
        self.accept("arrow_right", self.move_cube, [Vec3(1, 0, 0)])
        
        self.move_speed = 0.1
    
    def move_cube(self, direction):
        self.cube_pos += direction * self.move_speed
        self.render.find("**/box").setPos(self.cube_pos)

app = main()
app.run()