

-- Criar tabelas da aplicação em Porto_DB
CREATE TABLE IF NOT EXISTS berths (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    is_occupied BOOLEAN DEFAULT FALSE,
    maintenance_until TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS ships (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    ship_type VARCHAR(50) NOT NULL,
    priority INT NOT NULL,
    service_duration INT NOT NULL,
    arrival_time TIMESTAMP NOT NULL,
    start_service_time TIMESTAMP NULL,
    end_service_time TIMESTAMP NULL,
    wait_time INT NULL,
    berth_id INT NULL REFERENCES berths(id)
);

CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_time TIMESTAMP NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    ship_id INT NULL REFERENCES ships(id),
    berth_id INT NULL REFERENCES berths(id)
);

CREATE TABLE IF NOT EXISTS statistics(
    id SERIAL PRIMARY KEY,
    snapshot_time TIMESTAMP NOT NULL,
    total_ships_handled INT NOT NULL,
    total_wait_time INT NOT NULL,
    total_service_time INT NOT NULL,
    avg_occupancy_percent FLOAT NOT NULL
);
