import time
import random
from datetime import datetime, timedelta
from colorama import init, Fore, Style
from tabulate import tabulate
from infrastructure.database import Database  # importa a classe que criamos

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
        self.id = None  # ID do banco

class AdvancedPortManager:
    def __init__(self, db: Database, berths_count=4, tick_seconds=1, new_ship_interval=5):
        self.db = db
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
        self.events = []

        # Manutenção dos cais
        self.berth_maintenance = [None] * berths_count

        # Inicializa berths no DB
        self.berth_ids = []
        for i in range(berths_count):
            berth_id = self.db.insert_berth(f"Cais-{i+1}")
            self.berth_ids.append(berth_id)

    def generate_random_ship(self):
        self.ship_counter += 1
        ship_types = [("Cargueiro", 1, 8), ("Tanker", 2, 10), ("Porta-Contêiner", 3, 12)]
        ship_type, priority, base_duration = random.choice(ship_types)
        service_duration = random.randint(base_duration-2, base_duration+3)
        ship_name = f"{ship_type}-{self.ship_counter}"
        ship = Ship(ship_name, ship_type, priority, service_duration)
        ship.id = self.db.insert_ship(ship.name, ship.ship_type, ship.priority, ship.service_duration, ship.arrival_time)
        return ship

    def add_ship(self, ship):
        self.waiting_queue.append(ship)
        color = Fore.RED if ship.priority == 3 else Fore.YELLOW if ship.priority == 2 else Fore.GREEN
        msg = f"{datetime.now().strftime('%H:%M:%S')} - {color}Navio {ship.name} chegou (P{ship.priority}){Style.RESET_ALL}"
        self.events.append(msg)
        self.db.insert_event(datetime.now(), "ARRIVAL", msg, ship_id=ship.id)

    def process_queue(self):
        self.waiting_queue.sort(key=lambda s: (-s.priority, s.arrival_time))
        for i in range(self.berths_count):
            if self.berths[i] is None and self.berth_maintenance[i] is None and self.waiting_queue:
                next_ship = self.waiting_queue.pop(0)
                next_ship.start_service_time = datetime.now()
                self.berths[i] = next_ship
                self.db.update_ship_times(next_ship.id, start_service_time=next_ship.start_service_time, berth_id=self.berth_ids[i])
                msg = f"{datetime.now().strftime('%H:%M:%S')} - {Fore.CYAN}Navio {next_ship.name} atracou no cais {i+1}"
                self.events.append(msg)
                self.db.insert_event(datetime.now(), "DOCK", msg, ship_id=next_ship.id, berth_id=self.berth_ids[i])

    def update_berths(self):
        for i, ship in enumerate(self.berths):
            if self.berth_maintenance[i]:
                if datetime.now() >= self.berth_maintenance[i]:
                    self.berth_maintenance[i] = None
                    msg = f"{datetime.now().strftime('%H:%M:%S')} - {Fore.MAGENTA}Cais {i+1} voltou a ficar disponível"
                    self.events.append(msg)
                    self.db.update_berth(self.berth_ids[i], is_occupied=False, maintenance_until=None)
                    self.db.insert_event(datetime.now(), "MAINTENANCE_END", msg, berth_id=self.berth_ids[i])
                continue

            if ship:
                elapsed = (datetime.now() - ship.start_service_time).total_seconds()
                self.berth_occupancy_time[i] += self.tick_seconds
                if random.random() < 0.01:
                    ship.service_duration += random.randint(1,3)
                    msg = f"{datetime.now().strftime('%H:%M:%S')} - {Fore.YELLOW}Navio {ship.name} sofreu atraso no serviço (+{ship.service_duration} segundos)"
                    self.events.append(msg)
                    self.db.insert_event(datetime.now(), "DELAY", msg, ship_id=ship.id, berth_id=self.berth_ids[i])

                if elapsed >= ship.service_duration:
                    ship.end_service_time = datetime.now()
                    wait_time = (ship.start_service_time - ship.arrival_time).total_seconds()
                    self.total_wait_time += wait_time
                    self.total_service_time += ship.service_duration
                    self.total_ships_handled += 1
                    self.history.append(ship)
                    msg = f"{datetime.now().strftime('%H:%M:%S')} - {Fore.YELLOW}Navio {ship.name} deixou o cais {i+1} (Espera: {int(wait_time)}s, Serviço: {ship.service_duration}s)"
                    self.events.append(msg)
                    self.db.update_ship_times(ship.id, end_service_time=ship.end_service_time, wait_time=wait_time)
                    self.db.insert_event(datetime.now(), "DEPARTURE", msg, ship_id=ship.id, berth_id=self.berth_ids[i])
                    self.berths[i] = None

                    if random.random() < 0.05:
                        self.berth_maintenance[i] = datetime.now() + timedelta(seconds=random.randint(5,10))
                        msg = f"{datetime.now().strftime('%H:%M:%S')} - {Fore.MAGENTA}Cais {i+1} entrou em manutenção temporária"
                        self.events.append(msg)
                        self.db.update_berth(self.berth_ids[i], maintenance_until=self.berth_maintenance[i])
                        self.db.insert_event(datetime.now(), "MAINTENANCE_START", msg, berth_id=self.berth_ids[i])

    def run(self):
        try:
            while True:
                now = datetime.now()
                interval = self.new_ship_interval + random.randint(-2,2)
                if (now - self.last_ship_time).total_seconds() >= interval:
                    self.add_ship(self.generate_random_ship())
                    self.last_ship_time = now

                self.update_berths()
                self.process_queue()
                self.print_dashboard()
                self.save_statistics()
                time.sleep(self.tick_seconds)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nSimulação finalizada pelo usuário.")
            print(Fore.CYAN + f"Histórico de navios atendidos: {len(self.history)}")
            self.print_ship_history(last_n=10)
            self.db.close()

    def print_ship_history(self, last_n=10):
        table = []
        for ship in self.history[-last_n:]:
            wait_time = int((ship.start_service_time - ship.arrival_time).total_seconds())
            table.append([ship.name, ship.ship_type, ship.priority, wait_time, ship.service_duration])
        print(tabulate(table, headers=["Navio", "Tipo", "Prioridade", "Espera(s)", "Serviço(s)"], tablefmt="grid"))

    def print_dashboard(self):
        print("\033c", end="")
        print(Style.BRIGHT + "--- PORTO DE SINES: DASHBOARD REAL-TIME ---\n")
        uptime = (datetime.now() - self.start_time).total_seconds()

        for i, ship in enumerate(self.berths):
            if self.berth_maintenance[i]:
                remaining = int((self.berth_maintenance[i] - datetime.now()).total_seconds())
                print(Fore.MAGENTA + f"Cais {i+1}: MANUTENÇÃO ({remaining}s restantes)")
            elif ship:
                remaining = max(0, int(ship.service_duration - (datetime.now() - ship.start_service_time).total_seconds()))
                print(Fore.CYAN + f"Cais {i+1}: {ship.name} ({remaining}s restantes)")
            else:
                print(Fore.GREEN + f"Cais {i+1}: Livre")

        queue_info = []
        for s in self.waiting_queue:
            color = Fore.RED if s.priority == 3 else Fore.YELLOW if s.priority == 2 else Fore.GREEN
            queue_info.append(f"{color}{s.name}(P{s.priority}){Style.RESET_ALL}")
        print("\nFila de espera: " + ", ".join(queue_info))

        avg_wait = (self.total_wait_time / self.total_ships_handled) if self.total_ships_handled else 0
        avg_service = (self.total_service_time / self.total_ships_handled) if self.total_ships_handled else 0
        occupancy = [t / uptime * 100 for t in self.berth_occupancy_time]
        avg_occupancy = sum(occupancy) / self.berths_count

        print(Fore.MAGENTA + f"\nTotal de navios atendidos: {self.total_ships_handled}")
        print(Fore.MAGENTA + f"Tempo médio de espera: {avg_wait:.1f}s | Tempo médio de serviço: {avg_service:.1f}s")
        print(Fore.MAGENTA + f"Ocupação média dos cais: {avg_occupancy:.1f}%")

        print(Fore.YELLOW + "\nÚltimos eventos:")
        for e in self.events[-5:]:
            print(f"  {e}")

    def save_statistics(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        occupancy = [t / uptime * 100 for t in self.berth_occupancy_time]
        avg_occupancy = sum(occupancy) / self.berths_count
        self.db.insert_statistics(datetime.now(), self.total_ships_handled, self.total_wait_time, self.total_service_time, avg_occupancy)
