
--  DATABASE 

CREATE DATABASE crime_db1;
USE crime_db1;

--  MAIN TABLE

CREATE TABLE crimes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Open'
);
--  LOG TABLE
CREATE TABLE crime_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    crime_id INT,
    action VARCHAR(50),
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crime_id) REFERENCES crimes(id)
);
--  INDEX
CREATE INDEX idx_location ON crimes(location);
-- view
CREATE VIEW crime_view AS
SELECT id, type, location, date, status FROM crimes;

-- STORED PROCEDURE
DELIMITER $$

CREATE PROCEDURE add_crime_proc(
    IN p_type VARCHAR(100),
    IN p_location VARCHAR(100),
    IN p_date DATE
)
BEGIN
    INSERT INTO crimes(type, location, date)
    VALUES(p_type, p_location, p_date);
END $$

DELIMITER ;

--  FUNCTION
DELIMITER $$

CREATE FUNCTION get_crime_count()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total FROM crimes;
    RETURN total;
END $$

DELIMITER ;

--  TRIGGER
DELIMITER $$

CREATE TRIGGER after_crime_insert
AFTER INSERT ON crimes
FOR EACH ROW
BEGIN
    INSERT INTO crime_log(crime_id, action)
    VALUES(NEW.id, 'INSERT');
END $$

DELIMITER ;

--  CURSOR
DELIMITER $$

CREATE PROCEDURE cursor_demo()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE c_type VARCHAR(100);

    DECLARE cur CURSOR FOR SELECT type FROM crimes;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO c_type;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SELECT c_type;
    END LOOP;

    CLOSE cur;
END $$

DELIMITER ;


-- ALL IMPORTANT QUERIES

SELECT * FROM crimes;

SELECT * FROM crimes WHERE location = 'pune';

SELECT * FROM crimes WHERE location LIKE 'p%';

SELECT * FROM crimes 
WHERE date BETWEEN '2026-01-01' AND '2026-12-31';

SELECT * FROM crimes ORDER BY date ASC;

SELECT location, COUNT(*) 
FROM crimes 
GROUP BY location;

SELECT location, COUNT(*) 
FROM crimes 
GROUP BY location 
HAVING COUNT(*) > 1;

SELECT COUNT(*) AS total_crimes,
       MAX(id) AS max_id,
       MIN(id) AS min_id,
       AVG(id) AS avg_id
FROM crimes;

SELECT * FROM crimes 
WHERE id > (SELECT AVG(id) FROM crimes);

--  DATE FUNCTIONS

SELECT CURDATE();
SELECT NOW();

SELECT * FROM crimes WHERE YEAR(date) = 2026;
SELECT * FROM crimes WHERE MONTH(date) = 4;
SELECT * FROM crimes WHERE DAY(date) = 10;

SELECT DATEDIFF(CURDATE(), date) FROM crimes;
SELECT DATE_ADD(date, INTERVAL 5 DAY) FROM crimes;

--  EXECUTION
CALL add_crime_proc('theft', 'pune', '2026-04-10');
SELECT get_crime_count();
CALL cursor_demo();