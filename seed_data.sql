-- =============================================================
--  MaskDetector — Seed Data
--  Run after database_setup.sql to insert default records.
--
--  Usage:
--    mysql -u <user> -p <database_name> < seed_data.sql
-- =============================================================

-- -------------------------------------------------------------
-- login  (default password for both accounts: Admin@123)
--   Hash: PBKDF2-HMAC-SHA256, 100 000 iterations
--   CHANGE these passwords immediately after first login.
-- -------------------------------------------------------------
INSERT IGNORE INTO login (username, email, password, role) VALUES
    ('Super Admin', 'superadmin@maskdetector.com',
     'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6:1f9ba3c98fe83cfc01de88ae301f5a8c1a59649681b7b2b750ee4b71ce60a3ae',
     'Super Admin'),
    ('Admin User',  'admin@maskdetector.com',
     'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6:1f9ba3c98fe83cfc01de88ae301f5a8c1a59649681b7b2b750ee4b71ce60a3ae',
     'Admin');

-- -------------------------------------------------------------
-- surv_loc
-- -------------------------------------------------------------
INSERT IGNORE INTO surv_loc (s_loc) VALUES
    ('Main Gate'),
    ('Canteen'),
    ('Library'),
    ('Parking Lot'),
    ('Reception');

-- -------------------------------------------------------------
-- complaint  (depends on surv_loc rows above)
-- -------------------------------------------------------------
INSERT IGNORE INTO complaint (name, mobile, email, report, s_loc, status) VALUES
    ('Ravi Kumar',   '9876543210', 'ravi@example.com',
     'People entering without masks at the main gate.', 'Main Gate', 'Pending'),
    ('Priya Sharma', '9123456780', 'priya@example.com',
     'No mask enforcement observed near canteen area.', 'Canteen', 'Pending'),
    ('Arjun Mehta',  '9988776655', 'arjun@example.com',
     'Students in library not wearing masks.', 'Library', 'Surviellance done successfully');

-- -------------------------------------------------------------
-- survielance  (depends on surv_loc rows above)
-- -------------------------------------------------------------
INSERT IGNORE INTO survielance (s_loc, dos, start_time, end_time, with_mask, without) VALUES
    ('Main Gate',   '2024-01-15', '09:00:00', '09:30:00', '87.5 %', '12.5 %'),
    ('Canteen',     '2024-01-15', '12:00:00', '12:45:00', '72.0 %', '28.0 %'),
    ('Library',     '2024-01-16', '10:00:00', '10:20:00', '95.0 %',  '5.0 %'),
    ('Parking Lot', '2024-01-16', '08:30:00', '09:00:00', '60.0 %', '40.0 %'),
    ('Reception',   '2024-01-17', '11:00:00', '11:30:00', '100.0 %', '0.0 %');
