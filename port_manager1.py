import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
import uuid
from enum import Enum

from DataManager import generate__vessel_data


class BerthStatus(Enum):
    FREE = "free"
    BUSY = "busy"
    MAINTENANCE = "maintenance"


class ShipType(Enum):
    CONTAINER = "Container"
    TANKER = "Tanker"
    GERAL = "Carga Geral"


# ------------------------ Helpers de coerção ------------------------

def _coerce_ship_type(value: Union[str, ShipType]) -> ShipType:
    if isinstance(value, ShipType):
        return value
    if isinstance(value, str):
        # normaliza espaços/acentos comuns
        txt = value.strip().lower()
        mapa = {
            "container": ShipType.CONTAINER,
            "tanker": ShipType.TANKER,
            "carga geral": ShipType.GERAL,
            "geral": ShipType.GERAL,
        }
        if txt in mapa:
            return mapa[txt]
        # tenta casar com os .value do enum
        for st in ShipType:
            if txt == st.value.lower():
                return st
    raise ValueError(f"ship_type inválido: {value!r}")


def _coerce_arrival_time(value: Union[str, datetime]) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        # tenta formatos mais comuns
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
                    "%Y/%m/%d %H:%M:%S", "%d-%m-%Y %H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                pass
    raise ValueError(f"arrival_time inválido: {value!r}")


def _coerce_service_duration(value: Any) -> timedelta:
    """
    Aceita:
      - timedelta -> retorna como está
      - int/float (horas) -> timedelta(hours=value)
      - 'HH:MM' ou 'HH:MM:SS' -> duração
    NÃO aceita datetime completo (data+hora) porque isso é um instante, não duração.
    """
    if isinstance(value, timedelta):
        return value
    if isinstance(value, (int, float)):
        return timedelta(hours=float(value))
    if isinstance(value, str):
        parts = value.strip().split(":")
        if len(parts) in (2, 3) and all(p.isdigit() for p in parts):
            h = int(parts[0])
            m = int(parts[1])
            s = int(parts[2]) if len(parts) == 3 else 0
            return timedelta(hours=h, minutes=m, seconds=s)
    raise ValueError(
        "estimated_service_hours inválido. Use timedelta, número de horas (float/int), "
        "ou string 'HH:MM[:SS]'. Recebido: %r" % (value,)
    )


# ------------------------ Modelos ------------------------

@dataclass
class Ship:
    """Classe representando um navio"""
    id: str
    name: str
    ship_type: ShipType
    arrival_time: datetime
    estimated_service_hours: timedelta
    priority: int = 1  # 1=normal, 2=alta, 3=crítica

    def __init__(self, ship_data: Dict[str, Any]):
        self.id = ship_data["id"]
        self.name = ship_data["name"]
        self.ship_type = _coerce_ship_type(ship_data["ship_type"])
        self.arrival_time = _coerce_arrival_time(ship_data["arrival_time"])
        self.estimated_service_hours = _coerce_service_duration(ship_data["estimated_service_hours"])
        self.priority = int(ship_data.get("priority", 1))

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class Berth:
    """Classe representando um cais"""
    num_cais: int
    ship_id: Optional[str] = None
    entry_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    status: BerthStatus = BerthStatus.FREE

    def is_available(self) -> bool:
        return self.status == BerthStatus.FREE

    def assign_ship(self, ship: Ship, current_time: datetime):
        """Atribui navio ao cais"""
        self.ship_id = ship.id
        self.entry_time = current_time
        self.estimated_completion = current_time + ship.estimated_service_hours
        self.status = BerthStatus.BUSY

    def release_ship(self):
        """Libera o cais"""
        self.ship_id = None
        self.entry_time = None
        self.estimated_completion = None
        self.status = BerthStatus.FREE


class PortManager:
    """Sistema de gestão do porto"""

    def __init__(self, num_berths: int = 4):
        self.berths = [Berth(num_cais=i + 1) for i in range(num_berths)]
        self.waiting_queue: List[Ship] = []   # Fila de espera
        self.ships_served: List[Dict[str, Any]] = []   # Histórico
        self.current_time = datetime.now()

    def add_ship_to_queue(self, ship: Ship) -> str:
        """Adiciona navio à fila de espera (chegada = agora)"""
        ship.arrival_time = self.current_time
        self.waiting_queue.append(ship)
        return f"Navio {ship.name} ({ship.id}) adicionado à fila. Posição: {len(self.waiting_queue)}"

    def process_queue(self) -> List[str]:
        """Processa a fila - move navios para cais livres"""
        messages = []
        available_berths = [berth for berth in self.berths if berth.is_available()]

        while self.waiting_queue and available_berths:
            # prioridade desc, depois por chegada (FIFO)
            self.waiting_queue.sort(key=lambda ship: (-ship.priority, ship.arrival_time))

            ship = self.waiting_queue.pop(0)
            berth = available_berths.pop(0)

            berth.assign_ship(ship, self.current_time)

            # Tempo de espera -> Xh:Ym
            waiting_seconds = (self.current_time - ship.arrival_time).total_seconds()
            wait_h = int(waiting_seconds // 3600)
            wait_m = int((waiting_seconds % 3600) // 60)

            # Tempo de serviço -> Xh:Ym
            service_seconds = ship.estimated_service_hours.total_seconds()
            serv_h = int(service_seconds // 3600)
            serv_m = int((service_seconds % 3600) // 60)

            # Conclusão prevista
            completion_time = berth.estimated_completion.strftime("%Y-%m-%d %H:%M:%S")

            messages.append(
                f"🛳️ ✅ Navio {ship.name} ({ship.id}) atracou no Cais {berth.num_cais}. "
                f"⏱️ Espera: {wait_h}h:{wait_m:02d} | "
                f"⚓ Serviço previsto: {serv_h}h:{serv_m:02d} | "
                f"📅 Conclusão: {completion_time}"
            )

        return messages

    def complete_service(self, berth_num: int) -> str:
        """Finaliza atendimento de um navio"""
        if berth_num < 1 or berth_num > len(self.berths):
            return f"❌ Cais {berth_num} não existe!"

        berth = self.berths[berth_num - 1]

        if berth.status != BerthStatus.BUSY:
            return f"❌ Cais {berth_num} não está ocupado!"

        # Tempo efetivo de serviço
        service_time_h = (self.current_time - berth.entry_time).total_seconds() / 3600

        served_ship = {
            'ship_id': berth.ship_id,
            'berth': berth_num,
            'entry_time': berth.entry_time,
            'departure_time': self.current_time,
            'service_hours': service_time_h
        }
        self.ships_served.append(served_ship)

        ship_id = berth.ship_id
        berth.release_ship()

        # Processa fila após liberar
        queue_messages = self.process_queue()

        msg = f"🚢 Navio {ship_id} saiu do Cais {berth_num}. Tempo de serviço: {service_time_h:.1f}h"
        if queue_messages:
            msg += "\n" + "\n".join(queue_messages)
        return msg

    def advance_time(self, hours: float):
        """Avança o tempo do sistema e libera cais automaticamente quando concluído"""
        self.current_time += timedelta(hours=hours)
        messages = []
        for berth in self.berths:
            if (berth.status == BerthStatus.BUSY and
                berth.estimated_completion and
                self.current_time >= berth.estimated_completion):
                messages.append(self.complete_service(berth.num_cais))
        return messages

    def get_berths_status(self) -> pd.DataFrame:
        """Retorna status atual dos cais"""
        berths_data = []
        for berth in self.berths:
            if berth.status == BerthStatus.BUSY:
                remaining_hours = 0.0
                if berth.estimated_completion:
                    remaining_time = berth.estimated_completion - self.current_time
                    remaining_hours = max(0.0, remaining_time.total_seconds() / 3600)
                berths_data.append({
                    'Num_Cais': berth.num_cais,
                    'Status': 'BUSY',
                    'Ship_ID': berth.ship_id,
                    'Entrada': berth.entry_time.strftime('%H:%M') if berth.entry_time else '',
                    'Previsão_Saída': berth.estimated_completion.strftime('%H:%M') if berth.estimated_completion else '',
                    'Tempo_Restante': f"{remaining_hours:.1f}h"
                })
            else:
                berths_data.append({
                    'Num_Cais': berth.num_cais,
                    'Status': 'FREE',
                    'Ship_ID': '-',
                    'Entrada': '-',
                    'Previsão_Saída': '-',
                    'Tempo_Restante': '-'
                })
        return pd.DataFrame(berths_data)

    def get_queue_status(self) -> pd.DataFrame:
        """Retorna status da fila de espera"""
        if not self.waiting_queue:
            return pd.DataFrame({'Mensagem': ['Fila vazia']})

        queue_data = []
        for i, ship in enumerate(self.waiting_queue):
            waiting_time_h = (self.current_time - ship.arrival_time).total_seconds() / 3600
            queue_data.append({
                'Posição': i + 1,
                'Ship_ID': ship.id,
                'Nome': ship.name,
                'Tipo': ship.ship_type.value,
                'Prioridade': ship.priority,
                'Tempo_Espera': f"{waiting_time_h:.1f}h",
                'Chegada': ship.arrival_time.strftime('%H:%M')
            })
        return pd.DataFrame(queue_data)

    def get_queue_summary(self) -> Dict[str, Any]:
        """Resumo inteligente da fila"""
        if not self.waiting_queue:
            return {"status": "empty"}

        type_count: Dict[str, int] = {}
        for ship in self.waiting_queue:
            key = ship.ship_type.value
            type_count[key] = type_count.get(key, 0) + 1

        next_ship = self.waiting_queue[0] if self.waiting_queue else None
        avg_wait = sum(
            (self.current_time - ship.arrival_time).total_seconds() / 3600
            for ship in self.waiting_queue
        ) / len(self.waiting_queue)

        return {
            "total_waiting": len(self.waiting_queue),
            "by_type": type_count,
            "next_ship": next_ship.name if next_ship else None,
            "avg_waiting_time": avg_wait
        }

    def check_alerts(self) -> List[str]:
        """Verifica situações que precisam atenção"""
        alerts = []

        if len(self.waiting_queue) > 6:
            alerts.append("🚨 FILA CRÍTICA: Mais de 6 navios esperando!")

        busy_berths = sum(1 for b in self.berths if b.status == BerthStatus.BUSY)
        if busy_berths == len(self.berths) and self.waiting_queue:
            alerts.append("⚠️ PORTO SATURADO: Todos os cais ocupados!")

        for ship in self.waiting_queue:
            waiting_hours = (self.current_time - ship.arrival_time).total_seconds() / 3600
            if waiting_hours > 12:
                alerts.append(f"⏰ {ship.name} esperando há {waiting_hours:.1f}h!")

        return alerts

    def get_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard completo do sistema"""
        busy_berths = sum(1 for b in self.berths if b.status == BerthStatus.BUSY)
        return {
            'current_time': self.current_time.strftime('%Y-%m-%d %H:%M'),
            'berths_status': self.get_berths_status(),
            'queue_status': self.get_queue_status(),
            'summary': {
                'Cais Ocupados': f"{busy_berths}/{len(self.berths)}",
                'Navios na Fila': len(self.waiting_queue),
                'Navios Atendidos Hoje': len(self.ships_served),
                'Utilização': f"{(busy_berths/len(self.berths)*100):.1f}%"
            }
        }


def main():
    porto = PortManager(num_berths=4)

    # criar navios (um de cada vez, simulando chegadas)
    for _ in range(10):
        ship_data = generate__vessel_data()  # dict vindo do DataManager
        # GARANTE que arrival_time existe; se não, define "agora" e deixa o add_ship_to_queue sobrescrever
        ship_data.setdefault("arrival_time", datetime.now())
        ship = Ship(ship_data)
        porto.add_ship_to_queue(ship)
        porto.advance_time(0.5)  # avança 30 min

    # processa fila inicial
    for msg in porto.process_queue():
        print(msg)



    # Mostra dashboard
    dashboard = porto.get_dashboard()
    print(f"\n📊 DASHBOARD - {dashboard['current_time']}")
    print("\n🏗️  STATUS DOS CAIS:")
    print(dashboard['berths_status'].to_string(index=False))

    print("\n⏳ FILA DE ESPERA:")
    print(dashboard['queue_status'].to_string(index=False))


    print("\n📈 RESUMO:")
    for key, value in dashboard['summary'].items():
        print(f"  • {key}: {value}")
    # Simula passagem de tempo
    print("\n⏰ AVANÇANDO TEMPO (6 horas)...")
    time_messages = porto.advance_time(6.0)
    for msg in time_messages:
        print(f"  {msg}")

    # Finaliza manualmente um serviço
    print("\n🔧 FINALIZANDO SERVIÇO NO CAIS 1...")
    message = porto.complete_service(1)
    print(f"  {message}")

     # Dashboard final
    final_dashboard = porto.get_dashboard()
    print(f"\n📊 DASHBOARD FINAL - {final_dashboard['current_time']}")
    print("\n🏗️  STATUS DOS CAIS:")
    print(final_dashboard['berths_status'].to_string(index=False))
    
    return porto

if __name__ == "__main__":
    main()
