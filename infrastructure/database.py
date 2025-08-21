import psycopg2
from datetime import datetime
from config import DatabaseConfig  #    

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=DatabaseConfig.host,
            database=DatabaseConfig.database,
            user=DatabaseConfig.user,
            password=DatabaseConfig.password   
        )
        self.cursor = self.conn.cursor()

    # --- Cais ---
    def insert_berth(self, name):
        self.cursor.execute("""
            INSERT INTO berths (name) VALUES (%s) RETURNING id
        """, (name,))
        berth_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return berth_id

    def update_berth(self, berth_id, is_occupied=None, maintenance_until=None):
        self.cursor.execute("""
            UPDATE berths
            SET is_occupied = COALESCE(%s, is_occupied),
                maintenance_until = COALESCE(%s, maintenance_until)
            WHERE id = %s
        """, (is_occupied, maintenance_until, berth_id))
        self.conn.commit()

    # --- Navios ---
    def insert_ship(self, name, ship_type, priority, service_duration, arrival_time):
        self.cursor.execute("""
            INSERT INTO ships (name, ship_type, priority, service_duration, arrival_time)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (name, ship_type, priority, service_duration, arrival_time))
        ship_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return ship_id

    def update_ship_times(self, ship_id, start_service_time=None, end_service_time=None, wait_time=None, berth_id=None):
        self.cursor.execute("""
            UPDATE ships
            SET start_service_time = COALESCE(%s, start_service_time),
                end_service_time = COALESCE(%s, end_service_time),
                wait_time = COALESCE(%s, wait_time),
                berth_id = COALESCE(%s, berth_id)
            WHERE id = %s
        """, (start_service_time, end_service_time, wait_time, berth_id, ship_id))
        self.conn.commit()

    # --- Eventos ---
    def insert_event(self, event_time, event_type, description, ship_id=None, berth_id=None):
        self.cursor.execute("""
            INSERT INTO events (event_time, event_type, description, ship_id, berth_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (event_time, event_type, description, ship_id, berth_id))
        self.conn.commit()

    # --- Estatísticas ---
    def insert_statistics(self, snapshot_time, total_ships_handled, total_wait_time, total_service_time, avg_occupancy_percent):
        self.cursor.execute("""
            INSERT INTO statistics (snapshot_time, total_ships_handled, total_wait_time, total_service_time, avg_occupancy_percent)
            VALUES (%s, %s, %s, %s, %s)
        """, (snapshot_time, total_ships_handled, total_wait_time, total_service_time, avg_occupancy_percent))
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
