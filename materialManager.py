class MaterialManager:
    def __init__(self):
        self.materials = {
            'wood': {'mass': 1.0, 'friction': 0.5, 'restitution': 0.2, 'color': (0.65, 0.5, 0.39, 1)},
            'metal': {'mass': 5.0, 'friction': 0.3, 'restitution': 0.1, 'color': (0.7, 0.7, 0.7, 1)},
            'stone': {'mass': 3.0, 'friction': 0.7, 'restitution': 0.05, 'color': (0.5, 0.5, 0.5, 1)},
        }

    def get_material_properties(self, material, size):
        properties = self.materials.get(material)
        return {
            'mass': properties['mass'] * size,
            'friction': properties['friction'],
            'restitution': properties['restitution'],
            'color': properties['color']
        }
