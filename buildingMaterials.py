# WIP

class BuildingMaterial:
    def __init__(self, name, density):
        self.name = name
        self.density = density  # Density in kg/m^3

wood = BuildingMaterial("Wood", 500)  # Density of wood: 500 kg/m^3
metal = BuildingMaterial("Metal", 8000)  # Density of metal: 8000 kg/m^3
bricks = BuildingMaterial("Bricks", 2000)  # Density of bricks: 2000 kg/m^3
