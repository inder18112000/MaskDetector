-- =============================================================
--  MaskDetector — Database Setup Script
--  Run once to create all required tables.
--
--  Usage:
--    mysql -u <user> -p <database_name> < database_setup.sql
-- =============================================================

-- -------------------------------------------------------------
-- 1. login
--    Stores admin accounts.
--    Roles: 'Super Admin' | 'Admin'
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS login (
    username VARCHAR(100)        NOT NULL,
    email    VARCHAR(100)        NOT NULL,
    password VARCHAR(200)        NOT NULL,  -- PBKDF2-HMAC-SHA256: salt_hex:hash_hex (~97 chars)
    role     VARCHAR(50)         NOT NULL,
    PRIMARY KEY (email)
);

-- -------------------------------------------------------------
-- 2. surv_loc
--    Master list of surveillance locations.
--    Admins add locations from the dashboard.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS surv_loc (
    s_loc VARCHAR(100) NOT NULL,
    PRIMARY KEY (s_loc)
);

-- -------------------------------------------------------------
-- 3. complaint
--    Complaints submitted by the public.
--    status is updated to 'Surviellance done successfully'
--    once the admin runs a surveillance session for that location.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS complaint (
    cid    INT          NOT NULL AUTO_INCREMENT,
    name   VARCHAR(100) NOT NULL,
    mobile VARCHAR(20)  NOT NULL,
    email  VARCHAR(100) NOT NULL,
    report TEXT         NOT NULL,
    s_loc  VARCHAR(100) NOT NULL,
    status VARCHAR(100) DEFAULT 'Pending',
    PRIMARY KEY (cid),
    FOREIGN KEY (s_loc) REFERENCES surv_loc(s_loc)
);

-- -------------------------------------------------------------
-- 4. survielance   (note: intentional spelling from original app)
--    One row per surveillance session recorded by an admin.
--    with_mask / without store percentage strings e.g. "87.5 %"
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS survielance (
    sid        INT          NOT NULL AUTO_INCREMENT,
    s_loc      VARCHAR(100) NOT NULL,
    dos        DATE         NOT NULL,
    start_time TIME         NOT NULL,
    end_time   TIME         NOT NULL,
    with_mask  VARCHAR(20)  NOT NULL,
    without    VARCHAR(20)  NOT NULL,
    PRIMARY KEY (sid),
    FOREIGN KEY (s_loc) REFERENCES surv_loc(s_loc)
);

-- =============================================================
--  Default / Seed Records
--  Insert after tables are created.
-- =============================================================

-- -------------------------------------------------------------
-- login  (default password: Admin@123 — CHANGE IMMEDIATELY)
--   Hash algorithm : PBKDF2-HMAC-SHA256, 100 000 iterations
--   To generate your own hash run:  python3 setup_admin.py
-- -------------------------------------------------------------
INSERT IGNORE INTO login (username, email, password, role) VALUES
    ('Super Admin', 'superadmin@maskdetector.com',
     'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6:1f9ba3c98fe83cfc01de88ae301f5a8c1a59649681b7b2b750ee4b71ce60a3ae',
     'Super Admin'),
    ('Admin User',  'admin@maskdetector.com',
     'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6:1f9ba3c98fe83cfc01de88ae301f5a8c1a59649681b7b2b750ee4b71ce60a3ae',
     'Admin');

-- -------------------------------------------------------------
-- surv_loc  (seed surveillance locations)
-- -------------------------------------------------------------
INSERT IGNORE INTO surv_loc (s_loc) VALUES
    ('Main Gate'),
    ('Canteen'),
    ('Library'),
    ('Parking Lot'),
    ('Reception');

-- -------------------------------------------------------------
-- complaint  (sample complaints for testing)
-- -------------------------------------------------------------
INSERT IGNORE INTO complaint (name, mobile, email, report, s_loc, status) VALUES
    ('Ravi Kumar',   '9876543210', 'ravi@example.com',
     'People entering without masks at the main gate.', 'Main Gate', 'Pending'),
    ('Priya Sharma', '9123456780', 'priya@example.com',
     'No mask enforcement observed near canteen area.', 'Canteen', 'Pending'),
    ('Arjun Mehta',  '9988776655', 'arjun@example.com',
     'Students in library not wearing masks.', 'Library', 'Surviellance done successfully');

-- -------------------------------------------------------------
-- survielance  (sample surveillance sessions)
-- -------------------------------------------------------------
INSERT IGNORE INTO survielance (s_loc, dos, start_time, end_time, with_mask, without) VALUES
    ('Main Gate',   '2024-01-15', '09:00:00', '09:30:00', '87.5 %', '12.5 %'),
    ('Canteen',     '2024-01-15', '12:00:00', '12:45:00', '72.0 %', '28.0 %'),
    ('Library',     '2024-01-16', '10:00:00', '10:20:00', '95.0 %', '5.0 %'),
    ('Parking Lot', '2024-01-16', '08:30:00', '09:00:00', '60.0 %', '40.0 %'),
    ('Reception',   '2024-01-17', '11:00:00', '11:30:00', '100.0 %', '0.0 %');

-- -------------------------------------------------------------
-- After running this script, update admin passwords by running:
--   python3 setup_admin.py
-- or change them via the Forgot Password flow in the app.
-- -------------------------------------------------------------
