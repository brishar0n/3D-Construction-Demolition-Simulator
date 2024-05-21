class DestructionMethod:
    def __init__(self, name, force):
        self.name = name
        self.force = force  # Force of destruction in newtons

wrecking_ball = DestructionMethod("Wrecking Ball", 100000)  # Example force
explosive = DestructionMethod("Explosive", 500000)  # Example force