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
        self.arrival_time = datetime.now()
        self.start_service_time = None
        self.end_service_time = None

class AdvancedPortManager:
    def __init__(self, berths_count=4, tick_seconds=1, new_ship_interval=5):
        self.berths_count = berths_count
        self.berths = [None] * berths_count
        self.waiting_queue = []
        self.tick_seconds = tick_seconds
        self.new_ship_interval = new_ship_interval
        self.last_ship_time = datetime.now()
        self.ship_counter = 0

        # Estatísticas
        self.total_ships_handled = 0
        self.total_wait_time = 0
        self.total_service_time = 0
        self.berth_occupancy_time = [0] * berths_count
        self.start_time = datetime.now()
        self.history = []

    # Geração de navios com tempos variados
    def generate_random_ship(self):
        self.ship_counter += 1
        ship_types = [("Cargueiro", 1, 8), ("Tanker", 2, 10), ("Porta-Contêiner", 3, 12)]
        ship_type, priority, base_duration = random.choice(ship_types)
        service_duration = random.randint(base_duration-2, base_duration+3)
        ship_name = f"{ship_type}-{self.ship_counter}"
        return Ship(ship_name, ship_type, priority, service_duration)

    # Adiciona navio à fila
    def add_ship(self, ship):
        self.waiting_queue.append(ship)
        print(Fore.GREEN + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {ship.name} chegou ao porto (Prioridade {ship.priority}).")

    # Processa fila de espera
    def process_queue(self):
        self.waiting_queue.sort(key=lambda s: (-s.priority, s.arrival_time))
        for i in range(self.berths_count):
            if self.berths[i] is None and self.waiting_queue:
                next_ship = self.waiting_queue.pop(0)
                next_ship.start_service_time = datetime.now()
                self.berths[i] = next_ship
                print(Fore.CYAN + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {next_ship.name} atracou no cais {i+1}.")

    # Atualiza cais e registra estatísticas
    def update_berths(self):
        for i, ship in enumerate(self.berths):
            if ship:
                elapsed = (datetime.now() - ship.start_service_time).total_seconds()
                self.berth_occupancy_time[i] += self.tick_seconds
                if elapsed >= ship.service_duration:
                    ship.end_service_time = datetime.now()
                    wait_time = (ship.start_service_time - ship.arrival_time).total_seconds()
                    self.total_wait_time += wait_time
                    self.total_service_time += ship.service_duration
                    self.total_ships_handled += 1
                    self.history.append(ship)
                    print(Fore.YELLOW + f"[{datetime.now().strftime('%H:%M:%S')}] Navio {ship.name} deixou o cais {i+1}. Tempo de espera: {int(wait_time)}s, serviço: {ship.service_duration}s")
                    self.berths[i] = None

    # Dashboard completo
    def print_dashboard(self):
        os.system('clear')
        print(Style.BRIGHT + "--- PORTO DE SINES: DASHBOARD REAL-TIME ---\n")
        uptime = (datetime.now() - self.start_time).total_seconds()
        # Estado dos cais
        for i, ship in enumerate(self.berths):
            if ship:
                remaining = max(0, int(ship.service_duration - (datetime.now() - ship.start_service_time).total_seconds()))
                print(Fore.CYAN + f"Cais {i+1}: {ship.name} ({remaining}s restantes)")
            else:
                print(Fore.GREEN + f"Cais {i+1}: Livre")
        # Fila
        queue_names = [f"{s.name}(P{s.priority})" for s in self.waiting_queue]
        print(Fore.RED + f"\nFila de espera: {queue_names}")

        # Estatísticas
        avg_wait = (self.total_wait_time / self.total_ships_handled) if self.total_ships_handled else 0
        avg_service = (self.total_service_time / self.total_ships_handled) if self.total_ships_handled else 0
        occupancy = [t / uptime * 100 for t in self.berth_occupancy_time]
        avg_occupancy = sum(occupancy) / self.berths_count

        print(Fore.MAGENTA + f"\nTotal de navios atendidos: {self.total_ships_handled}")
        print(Fore.MAGENTA + f"Tempo médio de espera: {avg_wait:.1f}s | Tempo médio de serviço: {avg_service:.1f}s")
        print(Fore.MAGENTA + f"Ocupação média dos cais: {avg_occupancy:.1f}%")
        # Previsão de ocupação (simples)
        predicted_free_cais = sum(1 for s in self.berths if s is None)
        print(Fore.YELLOW + f"Cais livres previstos para próxima entrada: {predicted_free_cais}\n")

    # Loop principal
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
            print(Fore.CYAN + f"Histórico de navios atendidos: {len(self.history)}")
            for ship in self.history[-10:]:  # últimos 10 navios
                print(f"{ship.name}: espera {int((ship.start_service_time - ship.arrival_time).total_seconds())}s, serviço {ship.service_duration}s")

# Rodar simulação
porto = AdvancedPortManager(berths_count=4, tick_seconds=1, new_ship_interval=6)
porto.run()
