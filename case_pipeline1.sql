CREATE DATABASE case_pipeline;
USE case_pipeline;

CREATE TABLE case_events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    case_id     INT,
    case_type   VARCHAR(50),
    stage       VARCHAR(50),
    entered_at  DATETIME,
    assigned_to VARCHAR(100)
);

CREATE TABLE stage_targets (
    stage VARCHAR(50),
    target_days INT
);

INSERT INTO stage_targets VALUES
('Intake', 3),
('Review', 7),
('Verification', 10),
('Approval', 5),
('Closed', 1);