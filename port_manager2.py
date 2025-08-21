import time
import random
from datetime import datetime, timedelta

class Ship:
    def __init__(self, name, ship_type, priority, arrival_time, service_duration):
        self.name = name
        self.ship_type = ship_type
        self.priority = priority
        self.arrival_time = arrival_time
        self.service_duration = service_duration
        self.start_service_time = None

class RealTimePortManager:
    def __init__(self, berths_count=4, tick_seconds=2, new_ship_interval=5):
        self.berths_count = berths_count
        self.berths = [None] * berths_count
        self.waiting_queue = []
        self.tick_seconds = tick_seconds
        self.new_ship_interval = new_ship_interval
        self.last_ship_time = datetime.now()
        self.current_time = datetime.now()
        self.ship_counter = 0

    def generate_random_ship(self):
        self.ship_counter += 1
        ship_types = [("Cargueiro", 1), ("Tanker", 2), ("Porta-Contêiner", 3)]
        ship_type, priority = random.choice(ship_types)
        service_duration = random.randint(5, 15)  # segundos para simplificação
        ship_name = f"{ship_type}-{self.ship_counter}"
        return Ship(ship_name, ship_type, priority, self.current_time, service_duration)

    def add_ship(self, ship: Ship):
        self.waiting_queue.append(ship)
        print(f"[{self.current_time.strftime('%H:%M:%S')}] Navio {ship.name} chegou ao porto (Prioridade {ship.priority}).")

    def process_queue(self):
        # Ordena a fila por prioridade e tempo de chegada
        self.waiting_queue.sort(key=lambda s: (-s.priority, s.arrival_time))
        for i in range(self.berths_count):
            if self.berths[i] is None and self.waiting_queue:
                next_ship = self.waiting_queue.pop(0)
                next_ship.start_service_time = self.current_time
                self.berths[i] = next_ship
                print(f"[{self.current_time.strftime('%H:%M:%S')}] Navio {next_ship.name} atracou no cais {i+1}.")

    def update_berths(self):
        for i, ship in enumerate(self.berths):
            if ship:
                elapsed = (self.current_time - ship.start_service_time).total_seconds()
                if elapsed >= ship.service_duration:
                    print(f"[{self.current_time.strftime('%H:%M:%S')}] Navio {ship.name} deixou o cais {i+1}.")
                    self.berths[i] = None

    def run_real_time(self):
        while True:
            self.current_time = datetime.now()
            # Chegada automática de navios
            if (self.current_time - self.last_ship_time).total_seconds() >= self.new_ship_interval:
                new_ship = self.generate_random_ship()
                self.add_ship(new_ship)
                self.last_ship_time = self.current_time

            self.update_berths()
            self.process_queue()
            self.print_dashboard()
            time.sleep(self.tick_seconds)

    def print_dashboard(self):
        print("\n--- Estado do Porto ---")
        for i, ship in enumerate(self.berths):
            status = f"{ship.name} ({ship.service_duration}s)" if ship else "Livre"
            print(f"Cais {i+1}: {status}")
        queue_names = [f"{s.name}(P{s.priority})" for s in self.waiting_queue]
        print(f"Fila de espera: {queue_names}")
        print("\n")

# Rodar a simulação
porto = RealTimePortManager(berths_count=4, tick_seconds=2, new_ship_interval=6)
porto.run_real_time()
