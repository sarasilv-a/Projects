class Vehicle:
    def __init__(self, name, peso,capacity, speed, fuel, fuel_efficiency):

        self.name = name
        self.peso=peso
        self.capacity = max(0, capacity)
        self.speed = max(0, speed)
        self.fuel = max(0, min(fuel, 100))  # Limita o combustível inicial entre 0 e 100
        self.fuel_efficiency = max(0, fuel_efficiency)  # Evita valores negativos

    def getName(self):
        return self.name

    def getPeso(self):
        return self.peso

    def setPeso(self,peso):
        self.peso=peso

    def getCapacity(self):
        return self.capacity

    def getSpeed(self):
        return self.speed

    def getFuel(self):
        return self.fuel

    def getFuelEfficiency(self):
        return self.fuel_efficiency

    def setFuelEfficiency(self, efficiency):
        self.fuel_efficiency = max(0, efficiency)

    def decreaseFuel(self, distance):

        fuel_consumption = distance * self.fuel_efficiency
        self.fuel = max(0, self.fuel - fuel_consumption)  # Garante que o combustível não fique negativo

    def refuel(self, amount):

        if amount < 0:
            raise ValueError("A quantidade de combustível para reabastecimento deve ser positiva.")
        self.fuel = min(100, self.fuel + amount)  # Limita o combustível ao máximo de 100 unidades

    def __str__(self):
        return (f"Vehicle(name={self.name}, capacity={self.capacity}kg, speed={self.speed}km/h, "
                f"fuel={self.fuel}/100, fuel_efficiency={self.fuel_efficiency} units/km)")

    def __repr__(self):
        return self.__str__()
