CREATE TABLE licenses (
    license_key TEXT PRIMARY KEY,
    user_id TEXT,
    purchase_date DATETIME,
    activation_date DATETIME,
    status TEXT,
    hardware_id TEXT
); 