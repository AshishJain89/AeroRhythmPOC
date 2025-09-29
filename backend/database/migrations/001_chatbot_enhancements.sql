-- Add new tables for chatbot functionality
CREATE TABLE crew_certification (
    id SERIAL PRIMARY KEY,
    crew_id INTEGER REFERENCES crew(id) ON DELETE CASCADE,
    cert_type VARCHAR(100) NOT NULL, -- 'license', 'type-rating', 'medical'
    aircraft_type VARCHAR(50),
    issue_date DATE NOT NULL,
    expiry_date DATE NOT NULL,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crew_training (
    id SERIAL PRIMARY KEY,
    crew_id INTEGER REFERENCES crew(id) ON DELETE CASCADE,
    course VARCHAR(200) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pairing (
    id SERIAL PRIMARY KEY,
    pairing_code VARCHAR(20) UNIQUE NOT NULL,
    origin VARCHAR(3) NOT NULL,
    destination VARCHAR(3) NOT NULL,
    sectors JSONB NOT NULL, -- Array of flight legs
    planned_start TIMESTAMP NOT NULL,
    planned_end TIMESTAMP NOT NULL,
    aircraft_type VARCHAR(50) NOT NULL,
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE leave_request (
    id SERIAL PRIMARY KEY,
    crew_id INTEGER REFERENCES crew(id) ON DELETE CASCADE,
    leave_start TIMESTAMP NOT NULL,
    leave_end TIMESTAMP NOT NULL,
    leave_type VARCHAR(50) NOT NULL, -- 'annual', 'sick', 'personal'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE weather_forecast (
    id SERIAL PRIMARY KEY,
    airport_code VARCHAR(3) NOT NULL,
    forecast_time TIMESTAMP NOT NULL,
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    severity VARCHAR(50) NOT NULL, -- 'low', 'medium', 'high', 'severe'
    conditions JSONB NOT NULL, -- temperature, visibility, wind, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE disruption_event (
    id SERIAL PRIMARY KEY,
    type VARCHAR(100) NOT NULL, -- 'weather', 'maintenance', 'atc', 'crew'
    severity VARCHAR(50) NOT NULL,
    affected_pairings JSONB, -- Array of pairing IDs
    description TEXT,
    detected_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    source VARCHAR(100),
    attributes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE credentials_audit_log (
    id SERIAL PRIMARY KEY,
    crew_id INTEGER REFERENCE crew(id) ON DELETE CASCADE,
    snapshot_time TIMESTAMP NOT NULL,
    activation_certificates JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for performance
CREATE INDEX idx_crew_certification_expiry ON crew_certification(expiry_date);
CREATE INDEX idx_crew_certification_crew ON crew_certification(crew_id);
CREATE INDEX idx_crew_training_valid ON crew_training(valid_to);
CREATE INDEX idx_leave_request_dates ON leave_request(leave_start, leave_end);
CREATE INDEX idx_weather_forecast_airport ON weather_forecast(airport_code, valid_from);
CREATE INDEX idx_pairing_dates ON pairing(planned_start, planned_end);
