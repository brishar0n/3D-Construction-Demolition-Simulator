from panda3d.core import Vec3, LPoint3f
from panda3d.bullet import BulletSphericalConstraint, BulletRigidBodyNode, BulletBoxShape, BulletSphereShape
import numpy as np
from direct.task import Task

class DestructionManager:
    def __init__(self, main_app):
        self.main_app = main_app

    def add_wrecking_ball(self):
        main_app = self.main_app

        ball_radius = 2.0
        ball_shape = BulletSphereShape(ball_radius)
        ball_node = BulletRigidBodyNode('WreckingBall')
        ball_node.setMass(50.0)
        ball_node.addShape(ball_shape)
        ball_node.setFriction(0.5)
        ball_node.setRestitution(0.2)
        ball_node.setLinearDamping(0.1)
        ball_node.setAngularDamping(0.1)

        ball_np = main_app.render.attachNewNode(ball_node)
        ball_np.setPos(0, 0, 3)
        main_app.physics_world.attachRigidBody(ball_node)

        model = main_app.loader.loadModel('models/misc/sphere')
        model.setScale(ball_radius / 2)
        model.setColor(0.5, 0.5, 0.5, 1)
        model.reparentTo(ball_np)

        anchor_shape = BulletBoxShape(Vec3(0.1, 0.1, 0.1))
        anchor_node = BulletRigidBodyNode('Anchor')
        anchor_node.addShape(anchor_shape)
        anchor_node.setMass(0)
        anchor_np = main_app.render.attachNewNode(anchor_node)
        anchor_np.setPos(0, 0, 10) 

        main_app.physics_world.attachRigidBody(anchor_node)

        constraint = BulletSphericalConstraint(anchor_node, ball_node, LPoint3f(0, 0, 0), LPoint3f(0, 0, 0))
        constraint.setPivotA(LPoint3f(0, 0, 0))
        constraint.setPivotB(LPoint3f(0, 0, -5))

        constraint.setDebugDrawSize(2.0)

        main_app.physics_world.attachConstraint(constraint)

        ball_node.applyCentralImpulse(Vec3(50, 0, 0))

    def trigger_explosion(self, position, force, radius):
        main_app = self.main_app

        if not main_app.physics_enabled:
            return

        for node in main_app.render.getChildren():
            if node.node().isOfType(BulletRigidBodyNode.getClassType()):
                node_position = node.getPos()
                distance_vector = node_position - position
                distance = np.linalg.norm([distance_vector.getX(), distance_vector.getY(), distance_vector.getZ()])

                if distance < radius:
                    if distance == 0:
                        direction = Vec3(1, 0, 0)
                    else:
                        direction = distance_vector / distance
                    
                    impulse_magnitude = force / (distance + 0.1)
                    impulse = direction * impulse_magnitude
                    
                    node.node().applyCentralImpulse(impulse)

    def drop_heavy_ball(self, position):
        main_app = self.main_app

        ball_radius = 1.0
        ball_shape = BulletSphereShape(ball_radius)
        ball_node = BulletRigidBodyNode('HeavyBall')
        ball_node.setMass(100.0)
        ball_node.addShape(ball_shape)
        ball_node.setFriction(0.5)
        ball_node.setRestitution(0.6)
        ball_node.setLinearDamping(0.1)
        ball_node.setAngularDamping(0.1)

        ball_np = main_app.render.attachNewNode(ball_node)
        ball_np.setPos(position + Vec3(0, 0, 10))
        main_app.physics_world.attachRigidBody(ball_node)

        model = main_app.loader.loadModel('models/misc/sphere')
        model.setScale(ball_radius)
        model.setColor(0.7, 0.2, 0.2, 1)
        model.reparentTo(ball_np)

    def trigger_earthquake(self):
        main_app = self.main_app

        def apply_earthquake(task):
            magnitude = 10
            duration = 5
            elapsed = task.time
            
            if elapsed > duration:
                main_app.placing_mode = 'building'
                return Task.done

            for node in main_app.render.getChildren():
                if node.node().isOfType(BulletRigidBodyNode.getClassType()):
                    impulse = Vec3(
                        np.random.uniform(-1, 1),
                        np.random.uniform(-1, 1),
                        0
                    ) * magnitude
                    node.node().applyCentralImpulse(impulse)
            return Task.cont

        main_app.placing_mode = 'earthquake'
        main_app.taskMgr.add(apply_earthquake, "earthquakeTask")
