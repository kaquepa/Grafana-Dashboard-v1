import time
import random
from datetime import datetime
import os
from colorama import init, Fore, Style

init(autoreset=True)

class Ship:
    def __init__(self, name, ship_type, priority, service_duration):
        self.name = name
        self.ship_type = ship_type
        self.priority = priority
        self.service_duration = service_duration
        self.start_service_time = None

class PortManager:
    def __init__(self, berths_count=4, tick_seconds=2, new_ship_interval=5):
        self.berths_count = berths_count
        self.berths = [None] * berths_count
        self.waiting_queue = []
        self.tick_seconds = tick_seconds
        self.new_ship_interval = new_ship_interval
        self.last_ship_time = datetime.now()
        self.ship_counter = 0
        self.total_ships_handled = 0

    def generate_random_ship(self):
        self.ship_counter += 1
        ship_types = [("Cargueiro", 1, 8), ("Tanker", 2, 10), ("Porta-Contêiner", 3, 12)]
        ship_type, priority, base_duration = random.choice(ship_types)
        service_duration = random.randint(base_duration-2, base_duration+3)
        ship_name = f"{ship_type}-{self.ship_counter}"
        return Ship(ship_name, ship_type, priority, service_duration)

    def add_ship(self, ship):
        self.waiting_queue.append(ship)
        print(Fore.GREEN + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {ship.name} chegou ao porto (Prioridade {ship.priority}).")

    def process_queue(self):
        self.waiting_queue.sort(key=lambda s: (-s.priority))
        for i in range(self.berths_count):
            if self.berths[i] is None and self.waiting_queue:
                next_ship = self.waiting_queue.pop(0)
                next_ship.start_service_time = datetime.now()
                self.berths[i] = next_ship
                print(Fore.CYAN + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {next_ship.name} atracou no cais {i+1}.")

    def update_berths(self):
        for i, ship in enumerate(self.berths):
            if ship:
                elapsed = (datetime.now() - ship.start_service_time).total_seconds()
                if elapsed >= ship.service_duration:
                    print(Fore.YELLOW + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {ship.name} deixou o cais {i+1}.")
                    self.berths[i] = None
                    self.total_ships_handled += 1

    def print_dashboard(self):
        os.system('clear')
        print(Style.BRIGHT + "--- ESTADO DO PORTO DE SINES ---\n")
        for i, ship in enumerate(self.berths):
            if ship:
                elapsed = (datetime.now() - ship.start_service_time).total_seconds()
                remaining = max(0, int(ship.service_duration - elapsed))
                print(Fore.CYAN + f"Cais {i+1}: {ship.name} ({remaining}s restantes)")
            else:
                print(Fore.GREEN + f"Cais {i+1}: Livre")
        queue_names = [f"{s.name}(P{s.priority})" for s in self.waiting_queue]
        print(Fore.RED + f"Fila de espera: {queue_names}")
        print(Fore.MAGENTA + f"Total de navios atendidos: {self.total_ships_handled}\n")

    def run(self):
        try:
            while True:
                now = datetime.now()
                if (now - self.last_ship_time).total_seconds() >= self.new_ship_interval:
                    self.add_ship(self.generate_random_ship())
                    self.last_ship_time = now

                self.update_berths()
                self.process_queue()
                self.print_dashboard()
                time.sleep(self.tick_seconds)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nSimulação finalizada pelo usuário.")

# Rodar simulação
porto = PortManager(berths_count=4, tick_seconds=2, new_ship_interval=6)
porto.run()
