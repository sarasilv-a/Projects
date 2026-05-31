import random
from Vehicle import Vehicle


class Node:
    def __init__(self, name, id=-1, priority=0, accessibility=None, delivery_deadline=None, suprimentosNecessarios=0):
        self.m_id = id
        self.m_name = str(name)
        self.m_priority = max(0, priority)
        self.m_accessibility = accessibility if accessibility is not None else []
        self.m_delivery_deadline = delivery_deadline
        self.m_weather = self.random_weather()
        self.suprimentosNecessarios = suprimentosNecessarios
        self.m_heuristica = self.definir_heuristica()

    def getHeuristica(self):
            return self.m_heuristica

    def setHeuristica(self, heuristica):
            self.m_heuristica = heuristica


    def definir_heuristica(self): #
        prioridade_factor = 1 / (1 + self.m_priority)  # Mais prioridade -> menor valor
        deadline_factor = self.m_delivery_deadline if self.m_delivery_deadline else float(
            'inf')  # Sem prazo -> menos impacto
        weather_impact = {
            "ensolarado": 1.0,
            "nublado": 1.2,
            "chuva": 1.5,
            "chuva intensa": 2.0,
            "neve": 3.0
        }
        weather_factor = weather_impact.get(self.m_weather.lower(), 1.0)  # Fator baseado no clima

        # Combina os fatores em uma heurística ponderada
        heuristica = (prioridade_factor * 10) + (deadline_factor/100) * weather_factor
        return heuristica

    def getName(self):
        return self.m_name

    def getsuprimentosNecessarios(self):
        return self.suprimentosNecessarios

    def getWeather(self):
        return self.m_weather

    def getId(self):
        return self.m_id

    def getPriority(self):
        return self.m_priority

    def getAccessibility(self):
        return self.m_accessibility

    def getDeliveryDeadline(self):
        return self.m_delivery_deadline

    def setName(self, name):
        self.m_name = str(name)

    def setsuprimentosNecessarios(self, suprimentos):
        self.suprimentosNecessarios = suprimentos

    def setWeather(self, weather):
        self.m_weather = weather

    def setId(self, id):
        self.m_id = id

    def setPriority(self, priority):
        self.m_priority = max(0, priority)

    def setAccessibility(self, accessibility):
        if isinstance(accessibility, Vehicle):
            accessibility = [accessibility]
        elif not isinstance(accessibility, list):
            raise TypeError("O parâmetro deve ser uma instância de Vehicle ou uma lista de instâncias de Vehicle.")

        if any(not isinstance(vehicle, Vehicle) for vehicle in accessibility):
            raise TypeError("Todos os itens da lista devem ser instâncias de Vehicle.")

        self.m_accessibility = accessibility  # Armazena diretamente os objetos

    def setDeliveryDeadline(self, delivery_deadline):
        self.m_delivery_deadline = delivery_deadline

    def is_vehicle_allowed(self, vehicle):
        if vehicle.getName().lower() not in [v.lower() for v in self.m_accessibility]:
            print(f"O veículo {vehicle.getName()} não é permitido na vila {self.m_name}.")
            return False
        return True

    def random_weather(self):
        conditions = ["ensolarado", "chuva", "nublado", "chuva intensa", "neve"]
        return random.choice(conditions)

    def deliver_suprimentos(self, quantidade):
        if self.suprimentosNecessarios > 0:
            entregues = min(quantidade, self.suprimentosNecessarios)
            self.suprimentosNecessarios -= entregues
            return entregues
        return 0

    def get_vehicle_by_name(self, vehicle_name):
        for vehicle in self.m_accessibility:
            if vehicle.getName().lower() == vehicle_name.lower():
                return vehicle
        print(f"Erro: Veículo '{vehicle_name}' não encontrado no nó '{self.m_name}'.")
        return None

    def __lt__(self, other):
        return self.m_priority < other.m_priority

    def __gt__(self, other):
        return self.m_priority > other.m_priority

    def __str__(self):
        return (f"Node(name={self.m_name}, id={self.m_id}, priority={self.m_priority}, "
                f"accessibility={self.m_accessibility}, delivery_deadline={self.m_delivery_deadline}, "
                f"weather={self.m_weather}, suprimentos necessários={self.suprimentosNecessarios})")

    def __repr__(self):
        return f"Node(name={self.m_name}, id={self.m_id})"

