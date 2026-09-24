-- ============================================================
-- ENGINEERS DAY 2026
-- FINAL DATABASE SCHEMA
-- ============================================================
-- Development setup
-- Run this script ONCE for a fresh database setup.
-- ============================================================


-- ============================================================
-- 1. DATABASE
-- ============================================================

CREATE DATABASE IF NOT EXISTS engineers_day
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE engineers_day;


-- ============================================================
-- 2. DROP OLD TABLES
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS team_members;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS otp_verifications;
DROP TABLE IF EXISTS games;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS admins;

SET FOREIGN_KEY_CHECKS = 1;


-- ============================================================
-- 3. ADMINS
-- ============================================================

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,

    username VARCHAR(100) NOT NULL UNIQUE,

    password_hash VARCHAR(255) NOT NULL,

    full_name VARCHAR(150) NOT NULL,

    role ENUM(
        'SUPER_ADMIN',
        'EVENT_ADMIN',
        'RESULT_ADMIN'
    ) NOT NULL DEFAULT 'SUPER_ADMIN',

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    last_login_at DATETIME NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- ============================================================
-- 4. STUDENTS
-- ============================================================

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id VARCHAR(50) NOT NULL UNIQUE,

    name VARCHAR(100) NOT NULL,

    email VARCHAR(150) NOT NULL UNIQUE,

    phone VARCHAR(20) NOT NULL UNIQUE,

    branch VARCHAR(100) NULL,

    section VARCHAR(50) NULL,

    year VARCHAR(20) NULL,

    email_verified BOOLEAN NOT NULL DEFAULT FALSE,

    phone_verified BOOLEAN NOT NULL DEFAULT FALSE,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_student_name (name),

    INDEX idx_student_branch (branch),

    INDEX idx_student_section (section)
);


-- ============================================================
-- 5. OTP VERIFICATIONS
-- ============================================================

CREATE TABLE otp_verifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NULL,

    destination VARCHAR(150) NOT NULL,

    destination_type ENUM(
        'EMAIL',
        'PHONE'
    ) NOT NULL,

    otp_hash VARCHAR(255) NOT NULL,

    expires_at DATETIME NOT NULL,

    attempts INT NOT NULL DEFAULT 0,

    max_attempts INT NOT NULL DEFAULT 5,

    verified BOOLEAN NOT NULL DEFAULT FALSE,

    verified_at DATETIME NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_otp_destination (destination),

    INDEX idx_otp_expires (expires_at),

    INDEX idx_otp_student (student_id),

    CONSTRAINT fk_otp_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE
);


-- ============================================================
-- 6. GAMES / EVENTS
-- ============================================================

CREATE TABLE games (
    id INT AUTO_INCREMENT PRIMARY KEY,

    game_name VARCHAR(150) NOT NULL UNIQUE,

    description TEXT NULL,

    prize_pool VARCHAR(100) NULL,

    requirements TEXT NULL,

    rules TEXT NULL,

    registration_mode ENUM(
        'INDIVIDUAL',
        'TEAM'
    ) NOT NULL DEFAULT 'INDIVIDUAL',

    team_min_size INT NOT NULL DEFAULT 1,

    team_max_size INT NOT NULL DEFAULT 1,

    event_date DATE NULL,

    start_time TIME NULL,

    end_time TIME NULL,

    block VARCHAR(100) NULL,

    floor VARCHAR(50) NULL,

    room VARCHAR(100) NULL,

    status ENUM(
        'UPCOMING',
        'REGISTRATION_OPEN',
        'REGISTRATION_CLOSED',
        'LIVE',
        'COMPLETED',
        'CANCELLED'
    ) NOT NULL DEFAULT 'UPCOMING',

    registration_open BOOLEAN NOT NULL DEFAULT TRUE,

    winner_certificate BOOLEAN NOT NULL DEFAULT TRUE,

    runner_up_certificate BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_game_status (status),

    INDEX idx_game_date (event_date),

    INDEX idx_game_registration (registration_open)
);


-- ============================================================
-- 7. INDIVIDUAL REGISTRATIONS
-- ============================================================

CREATE TABLE registrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    game_id INT NOT NULL,

    status ENUM(
        'REGISTERED',
        'CANCELLED',
        'APPROVED',
        'REJECTED'
    ) NOT NULL DEFAULT 'REGISTERED',

    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY unique_student_game (
        student_id,
        game_id
    ),

    INDEX idx_registration_student (student_id),

    INDEX idx_registration_game (game_id),

    INDEX idx_registration_status (status),

    CONSTRAINT fk_registration_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_registration_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE
);


-- ============================================================
-- 8. TEAMS
-- ============================================================

CREATE TABLE teams (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    game_id INT NOT NULL,

    team_name VARCHAR(150) NOT NULL,

    team_leader_id INT NOT NULL,

    status ENUM(
        'REGISTERED',
        'CANCELLED',
        'APPROVED',
        'REJECTED'
    ) NOT NULL DEFAULT 'REGISTERED',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_team_game (game_id),

    INDEX idx_team_leader (team_leader_id),

    UNIQUE KEY unique_team_name_per_game (
        game_id,
        team_name
    ),

    CONSTRAINT fk_team_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_team_leader
        FOREIGN KEY (team_leader_id)
        REFERENCES students(id)
        ON DELETE RESTRICT
);


-- ============================================================
-- 9. TEAM MEMBERS
-- ============================================================

CREATE TABLE team_members (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    team_id BIGINT NOT NULL,

    student_id INT NOT NULL,

    member_role ENUM(
        'LEADER',
        'MEMBER'
    ) NOT NULL DEFAULT 'MEMBER',

    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY unique_student_team (
        team_id,
        student_id
    ),

    INDEX idx_team_member_student (student_id),

    INDEX idx_team_member_team (team_id),

    CONSTRAINT fk_team_member_team
        FOREIGN KEY (team_id)
        REFERENCES teams(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_team_member_student
        FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE RESTRICT
);


-- ============================================================
-- 10. NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    game_id INT NULL,

    title VARCHAR(200) NOT NULL,

    message TEXT NOT NULL,

    notification_type ENUM(
        'GENERAL',
        'EVENT',
        'RESULT',
        'IMPORTANT'
    ) NOT NULL DEFAULT 'GENERAL',

    is_published BOOLEAN NOT NULL DEFAULT FALSE,

    published_at DATETIME NULL,

    expires_at DATETIME NULL,

    created_by INT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_notification_game (game_id),

    INDEX idx_notification_published (is_published),

    INDEX idx_notification_created (created_at),

    CONSTRAINT fk_notification_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_notification_admin
        FOREIGN KEY (created_by)
        REFERENCES admins(id)
        ON DELETE SET NULL
);


-- ============================================================
-- 11. RESULTS
-- ============================================================

CREATE TABLE results (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    game_id INT NOT NULL UNIQUE,

    winner VARCHAR(200) NULL,

    winner_student_id INT NULL,

    winner_team_id BIGINT NULL,

    runner_up VARCHAR(200) NULL,

    runner_up_student_id INT NULL,

    runner_up_team_id BIGINT NULL,

    winner_prize VARCHAR(100) NULL,

    runner_up_prize VARCHAR(100) NULL,

    winner_certificate BOOLEAN NOT NULL DEFAULT TRUE,

    runner_up_certificate BOOLEAN NOT NULL DEFAULT FALSE,

    result_details TEXT NULL,

    is_published BOOLEAN NOT NULL DEFAULT FALSE,

    published_at DATETIME NULL,

    published_by INT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_result_published (is_published),

    CONSTRAINT fk_result_game
        FOREIGN KEY (game_id)
        REFERENCES games(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_result_winner_student
        FOREIGN KEY (winner_student_id)
        REFERENCES students(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_result_winner_team
        FOREIGN KEY (winner_team_id)
        REFERENCES teams(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_result_runner_student
        FOREIGN KEY (runner_up_student_id)
        REFERENCES students(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_result_runner_team
        FOREIGN KEY (runner_up_team_id)
        REFERENCES teams(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_result_admin
        FOREIGN KEY (published_by)
        REFERENCES admins(id)
        ON DELETE SET NULL
);


-- ============================================================
-- 12. AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    admin_id INT NULL,

    action VARCHAR(100) NOT NULL,

    entity_type VARCHAR(100) NULL,

    entity_id BIGINT NULL,

    old_value TEXT NULL,

    new_value TEXT NULL,

    ip_address VARCHAR(45) NULL,

    user_agent TEXT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_audit_admin (admin_id),

    INDEX idx_audit_entity (
        entity_type,
        entity_id
    ),

    INDEX idx_audit_created (created_at),

    CONSTRAINT fk_audit_admin
        FOREIGN KEY (admin_id)
        REFERENCES admins(id)
        ON DELETE SET NULL
);


-- ============================================================
-- 13. INSERT 27 OFFICIAL EVENTS
-- ============================================================

INSERT INTO games
(
    game_name,
    description,
    prize_pool,
    requirements,
    rules,
    registration_mode,
    team_min_size,
    team_max_size,
    status,
    registration_open,
    winner_certificate,
    runner_up_certificate
)
VALUES

(
    'BGMI Tournament',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Tech Treasure Hunt',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Reverse Coding',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Business Idea Pitch',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Codeless Development',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Content Writing',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Mock Interview',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Data Visualization Using Dashboard',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Just A Minute (JAM)',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Rapid Fire',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'LOGO Design',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Tech Meme War',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Reasoning, Aptitude & GK Test',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Poster Making',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Web Wonder',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'AD - Mad Show',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'ChatGPT Prompt Challenge',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Coding & Debugging',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Pictionary',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Group Discussion',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Debate',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Project Presentation',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'PPT Presentation',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'SR Got Talent',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Capture the Flag (CTF)',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Free Fire (Online Game)',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
),

(
    'Hackathon',
    NULL,
    NULL,
    NULL,
    NULL,
    'INDIVIDUAL',
    1,
    1,
    'UPCOMING',
    TRUE,
    TRUE,
    FALSE
);


-- ============================================================
-- 14. STUDENT REGISTRY
-- ============================================================
-- Admin uploads student IDs here.
-- This is the "authorized list" of who can log in.
-- students table = actual login profile (after first login).
-- ============================================================

CREATE TABLE IF NOT EXISTS student_registry (
    id                  BIGSERIAL    PRIMARY KEY,

    student_id          VARCHAR(50)  NOT NULL UNIQUE,

    is_active           BOOLEAN      NOT NULL DEFAULT TRUE,

    claimed             BOOLEAN      NOT NULL DEFAULT FALSE,

    claimed_student_id  INT          NULL,

    imported_at         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    claimed_at          TIMESTAMP    NULL,

    CONSTRAINT fk_registry_student
        FOREIGN KEY (claimed_student_id)
        REFERENCES students(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_registry_student_id
    ON student_registry (student_id);

CREATE INDEX IF NOT EXISTS idx_registry_claimed
    ON student_registry (claimed);

CREATE INDEX IF NOT EXISTS idx_registry_active
    ON student_registry (is_active);


-- ============================================================
-- 15. PORTAL SETTINGS
-- ============================================================
-- Single-row settings table controlled by the admin panel.
-- id = 1 always (one row only).
-- ============================================================

CREATE TABLE IF NOT EXISTS portal_settings (
    id                      INT          PRIMARY KEY DEFAULT 1,

    portal_name             VARCHAR(200) NOT NULL DEFAULT 'Engineers Day 2026',

    event_date              DATE         NULL,

    portal_status           VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE'
                                CHECK (portal_status IN ('ACTIVE', 'MAINTENANCE')),

    registration_enabled    BOOLEAN      NOT NULL DEFAULT TRUE,

    student_login_enabled   BOOLEAN      NOT NULL DEFAULT TRUE,

    created_at              TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    updated_at              TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert the default single settings row
INSERT INTO portal_settings
(
    id,
    portal_name,
    event_date,
    portal_status,
    registration_enabled,
    student_login_enabled
)
VALUES
(
    1,
    'Engineers Day 2026',
    '2026-09-15',
    'ACTIVE',
    TRUE,
    TRUE
)
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 16. VERIFICATION
-- ============================================================

SELECT COUNT(*) AS total_events   FROM games;
SELECT COUNT(*) AS total_students FROM student_registry;


-- ============================================================
-- END
-- ============================================================