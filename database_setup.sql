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
-- 2. cities
--    Pre-defined city list. Admins can add more via the dashboard.
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cities (
    city_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (city_name)
);

-- -------------------------------------------------------------
-- 3. surv_loc
--    Master list of surveillance locations (3-level hierarchy).
--    s_loc  = "PlaceName — Area" (PK / FK anchor)
--    city   = city this location belongs to
--    place_name = institution / venue (e.g. "Sunrise Public School")
--    area   = sub-location within the place (e.g. "Main Gate")
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS surv_loc (
    s_loc      VARCHAR(200) NOT NULL,
    city       VARCHAR(100) NOT NULL DEFAULT '',
    place_name VARCHAR(200) NOT NULL DEFAULT '',
    area       VARCHAR(100) NOT NULL DEFAULT '',
    PRIMARY KEY (s_loc)
);

-- -------------------------------------------------------------
-- 4. complaint
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
-- 5. survielance   (note: intentional spelling from original app)
--    One row per surveillance session recorded by an admin.
--    with_mask / without store percentage strings e.g. "87.5 %"
-- -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS survielance (
    sid           INT          NOT NULL AUTO_INCREMENT,
    s_loc         VARCHAR(100) NOT NULL,
    dos           DATE         NOT NULL,
    start_time    TIME         NOT NULL,
    end_time      TIME         NOT NULL,
    with_mask     VARCHAR(20)  NOT NULL,
    without       VARCHAR(20)  NOT NULL,
    total_persons INT          NOT NULL DEFAULT 0,
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
-- cities  (pre-seeded Indian cities — admin can add more)
-- -------------------------------------------------------------
INSERT IGNORE INTO cities (city_name) VALUES
    ('Ahmedabad'), ('Amritsar'),  ('Bengaluru'), ('Chandigarh'), ('Chennai'),
    ('Delhi'),     ('Hyderabad'), ('Jaipur'),    ('Kolkata'),    ('Lucknow'),
    ('Mumbai'),    ('Noida'),     ('Patna'),      ('Pune'),       ('Surat');

-- -------------------------------------------------------------
-- surv_loc  (legacy Chandigarh locations + multi-city locations)
-- -------------------------------------------------------------
INSERT IGNORE INTO surv_loc (s_loc, city, place_name, area) VALUES
    ('Main Gate',   'Chandigarh', '', ''),
    ('Canteen',     'Chandigarh', '', ''),
    ('Library',     'Chandigarh', '', ''),
    ('Parking Lot', 'Chandigarh', '', ''),
    ('Reception',   'Chandigarh', '', '');

-- Proper multi-city locations (place_name + area hierarchy)
INSERT IGNORE INTO surv_loc (s_loc, city, place_name, area) VALUES
    ('AIIMS — Main Gate',              'Delhi',      'AIIMS',               'Main Gate'),
    ('Connaught Place — Metro Exit',   'Delhi',      'Connaught Place',     'Metro Exit'),
    ('India Gate — North Gate',        'Delhi',      'India Gate',          'North Gate'),
    ('CST Station — Entry Hall',       'Mumbai',     'CST Station',         'Entry Hall'),
    ('Marine Drive — Promenade',       'Mumbai',     'Marine Drive',        'Promenade'),
    ('BKC — Office Complex',           'Mumbai',     'BKC',                 'Office Complex'),
    ('Cubbon Park — East Gate',        'Bengaluru',  'Cubbon Park',         'East Gate'),
    ('Koramangala — Food Street',      'Bengaluru',  'Koramangala',         'Food Street'),
    ('Marina Beach — North End',       'Chennai',    'Marina Beach',        'North End'),
    ('T. Nagar — Shopping Complex',    'Chennai',    'T. Nagar',            'Shopping Complex'),
    ('Sector 17 — Plaza',              'Chandigarh', 'Sector 17',           'Plaza'),
    ('PGI — OPD Block',                'Chandigarh', 'PGI',                 'OPD Block');

-- -------------------------------------------------------------
-- complaint  (sample complaints with mixed statuses)
-- -------------------------------------------------------------
INSERT IGNORE INTO complaint (name, mobile, email, report, s_loc, status) VALUES
    ('Ravi Kumar',   '9876543210', 'ravi@example.com',
     'People entering without masks at the main gate.', 'Main Gate', 'Pending'),
    ('Priya Sharma', '9123456780', 'priya@example.com',
     'No mask enforcement observed near canteen area.', 'Canteen', 'Pending'),
    ('Arjun Mehta',  '9988776655', 'arjun@example.com',
     'Students in library not wearing masks.', 'Library', 'Surveillance Done');

-- Multi-city complaints
INSERT IGNORE INTO complaint (name, mobile, email, report, s_loc, status) VALUES
    ('Aditya Nair',  '9811122334', 'aditya.nair@example.com',
     'Visitors entering AIIMS without masks at the main gate.',
     'AIIMS — Main Gate',            'Pending'),
    ('Sunita Verma', '9922334455', 'sunita.verma@example.com',
     'Metro commuters ignoring mask rules at Connaught Place exit.',
     'Connaught Place — Metro Exit', 'Under Review'),
    ('Karan Singh',  '9033445566', 'karan.singh@example.com',
     'Tourist crowd near India Gate not wearing masks.',
     'India Gate — North Gate',      'Pending'),
    ('Meera Pillai', '9144556677', 'meera.pillai@example.com',
     'Train passengers at CST not following mask mandate.',
     'CST Station — Entry Hall',     'Surveillance Done'),
    ('Rohit Desai',  '9255667788', 'rohit.desai@example.com',
     'Evening walkers on Marine Drive not wearing masks.',
     'Marine Drive — Promenade',     'Pending'),
    ('Pooja Iyer',   '9366778899', 'pooja.iyer@example.com',
     'Office employees at BKC tech park not complying with mask policy.',
     'BKC — Office Complex',         'Under Review'),
    ('Vikram Reddy', '9477889900', 'vikram.reddy@example.com',
     'Park visitors at Cubbon Park ignoring mask guidelines.',
     'Cubbon Park — East Gate',      'Dismissed'),
    ('Anjali Bose',  '9588990011', 'anjali.bose@example.com',
     'Food stall visitors at Koramangala without masks.',
     'Koramangala — Food Street',    'Pending'),
    ('Suresh Menon', '9699001122', 'suresh.menon@example.com',
     'Beach-goers at Marina Beach North End not wearing masks.',
     'Marina Beach — North End',     'Surveillance Done'),
    ('Deepa Joshi',  '9700112233', 'deepa.joshi@example.com',
     'Shoppers at T. Nagar market area not wearing masks.',
     'T. Nagar — Shopping Complex',  'Pending'),
    ('Naveen Gupta', '9811223344', 'naveen.gupta@example.com',
     'Crowded Sector 17 plaza with very low mask compliance.',
     'Sector 17 — Plaza',            'Pending'),
    ('Ananya Das',   '9922334456', 'ananya.das@example.com',
     'OPD visitors at PGI not following mask protocol.',
     'PGI — OPD Block',              'Under Review');

-- -------------------------------------------------------------
-- survielance  (sample surveillance sessions with person counts)
-- -------------------------------------------------------------
INSERT IGNORE INTO survielance (s_loc, dos, start_time, end_time, with_mask, without, total_persons) VALUES
    ('Main Gate',   '2024-01-15', '09:00:00', '09:30:00', '87.5 %', '12.5 %', 0),
    ('Canteen',     '2024-01-15', '12:00:00', '12:45:00', '72.0 %', '28.0 %', 0),
    ('Library',     '2024-01-16', '10:00:00', '10:20:00', '95.0 %', '5.0 %',  0),
    ('Parking Lot', '2024-01-16', '08:30:00', '09:00:00', '60.0 %', '40.0 %', 0),
    ('Reception',   '2024-01-17', '11:00:00', '11:30:00', '100.0 %','0.0 %',  0);

-- Multi-city sessions with realistic person counts
INSERT IGNORE INTO survielance (s_loc, dos, start_time, end_time, with_mask, without, total_persons) VALUES
    ('AIIMS — Main Gate',            '2025-11-10', '08:00:00', '08:45:00', '91.0 %', '9.0 %',  44),
    ('Connaught Place — Metro Exit', '2025-11-12', '10:30:00', '11:15:00', '78.5 %', '21.5 %', 65),
    ('India Gate — North Gate',      '2025-11-14', '16:00:00', '16:30:00', '55.0 %', '45.0 %', 20),
    ('CST Station — Entry Hall',     '2025-11-15', '07:30:00', '08:30:00', '83.0 %', '17.0 %', 118),
    ('Marine Drive — Promenade',     '2025-11-18', '18:00:00', '18:45:00', '66.0 %', '34.0 %', 50),
    ('BKC — Office Complex',         '2025-11-20', '09:00:00', '09:30:00', '97.0 %', '3.0 %',  72),
    ('Cubbon Park — East Gate',      '2025-12-02', '07:00:00', '07:40:00', '89.0 %', '11.0 %', 36),
    ('Marina Beach — North End',     '2025-12-05', '17:00:00', '17:45:00', '62.0 %', '38.0 %', 85),
    ('Sector 17 — Plaza',            '2025-12-10', '11:00:00', '11:30:00', '75.0 %', '25.0 %', 28),
    ('PGI — OPD Block',              '2025-12-15', '08:30:00', '09:15:00', '94.0 %', '6.0 %',  51),
    ('Main Gate',                    '2024-03-05', '09:00:00', '09:30:00', '82.0 %', '18.0 %', 33),
    ('Canteen',                      '2024-03-06', '12:00:00', '12:30:00', '70.0 %', '30.0 %', 40),
    ('Library',                      '2024-03-07', '10:00:00', '10:20:00', '95.0 %', '5.0 %',  22);

-- -------------------------------------------------------------
-- After running this script, update admin passwords by running:
--   python3 setup_admin.py
-- or change them via the Forgot Password flow in the app.
-- -------------------------------------------------------------
