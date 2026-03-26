-- =============================================================
--  PAGILA SLAVE - MySQL
--  Proyecto: Sincronizador Master-Slave | TBD2
--  Base de datos: pagila_slave
-- =============================================================

CREATE DATABASE IF NOT EXISTS pagila_slave
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE pagila_slave;

--  TABLAS IN (MASTER → SLAVE)
--  El slave solo recibe estos datos, nunca los modifica.

CREATE TABLE IF NOT EXISTS actor (
    actor_id    SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(45)       NOT NULL,
    last_name   VARCHAR(45)       NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (actor_id)
);

CREATE TABLE IF NOT EXISTS category (
    category_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(25)      NOT NULL,
    last_update TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (category_id)
);

CREATE TABLE IF NOT EXISTS language (
    language_id TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        CHAR(20)         NOT NULL,
    last_update TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (language_id)
);

CREATE TABLE IF NOT EXISTS film (
    film_id              SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    title                VARCHAR(255)      NOT NULL,
    description          TEXT,
    release_year         YEAR,
    language_id          TINYINT UNSIGNED  NOT NULL,
    rental_duration      TINYINT UNSIGNED  NOT NULL DEFAULT 3,
    rental_rate          DECIMAL(4,2)      NOT NULL DEFAULT 4.99,
    length               SMALLINT UNSIGNED,
    replacement_cost     DECIMAL(5,2)      NOT NULL DEFAULT 19.99,
    rating               ENUM('G','PG','PG-13','R','NC-17') DEFAULT 'G',
    special_features     SET('Trailers','Commentaries','Deleted Scenes','Behind the Scenes'),
    last_update          TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (film_id),
    FOREIGN KEY (language_id) REFERENCES language(language_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS film_actor (
    actor_id    SMALLINT UNSIGNED NOT NULL,
    film_id     SMALLINT UNSIGNED NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (actor_id, film_id),
    FOREIGN KEY (actor_id) REFERENCES actor(actor_id)    ON UPDATE CASCADE,
    FOREIGN KEY (film_id)  REFERENCES film(film_id)      ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS film_category (
    film_id     SMALLINT UNSIGNED NOT NULL,
    category_id TINYINT UNSIGNED  NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (film_id, category_id),
    FOREIGN KEY (film_id)     REFERENCES film(film_id)         ON UPDATE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS country (
    country_id  SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    country     VARCHAR(50)       NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (country_id)
);

CREATE TABLE IF NOT EXISTS city (
    city_id     SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    city        VARCHAR(50)       NOT NULL,
    country_id  SMALLINT UNSIGNED NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (city_id),
    FOREIGN KEY (country_id) REFERENCES country(country_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS address (
    address_id  SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    address     VARCHAR(50)       NOT NULL,
    address2    VARCHAR(50),
    district    VARCHAR(20)       NOT NULL,
    city_id     SMALLINT UNSIGNED NOT NULL,
    postal_code VARCHAR(10),
    phone       VARCHAR(20)       NOT NULL,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (address_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS store (
    store_id         TINYINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    manager_staff_id TINYINT UNSIGNED  NOT NULL,
    address_id       SMALLINT UNSIGNED NOT NULL,
    last_update      TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (store_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS staff (
    staff_id    TINYINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    first_name  VARCHAR(45)       NOT NULL,
    last_name   VARCHAR(45)       NOT NULL,
    address_id  SMALLINT UNSIGNED NOT NULL,
    email       VARCHAR(50),
    store_id    TINYINT UNSIGNED  NOT NULL,
    active      TINYINT(1)        NOT NULL DEFAULT 1,
    username    VARCHAR(16)       NOT NULL,
    password    VARCHAR(40),
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (staff_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE,
    FOREIGN KEY (store_id)   REFERENCES store(store_id)     ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
    film_id      SMALLINT UNSIGNED  NOT NULL,
    store_id     TINYINT UNSIGNED   NOT NULL,
    last_update  TIMESTAMP          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (inventory_id),
    FOREIGN KEY (film_id)  REFERENCES film(film_id)   ON UPDATE CASCADE,
    FOREIGN KEY (store_id) REFERENCES store(store_id) ON UPDATE CASCADE
);

--  TABLAS OUT (SLAVE → MASTER)
--  El slave genera estos datos localmente y los sube al master.

CREATE TABLE IF NOT EXISTS customer (
    customer_id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    store_id    TINYINT UNSIGNED  NOT NULL,
    first_name  VARCHAR(45)       NOT NULL,
    last_name   VARCHAR(45)       NOT NULL,
    email       VARCHAR(50),
    address_id  SMALLINT UNSIGNED NOT NULL,
    active      TINYINT(1)        NOT NULL DEFAULT 1,
    create_date DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    FOREIGN KEY (address_id) REFERENCES address(address_id) ON UPDATE CASCADE,
    FOREIGN KEY (store_id)   REFERENCES store(store_id)     ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS rental (
    rental_id    INT               NOT NULL AUTO_INCREMENT,
    rental_date  DATETIME          NOT NULL,
    inventory_id MEDIUMINT UNSIGNED NOT NULL,
    customer_id  SMALLINT UNSIGNED  NOT NULL,
    return_date  DATETIME,
    staff_id     TINYINT UNSIGNED   NOT NULL,
    last_update  TIMESTAMP          NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (rental_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id) ON UPDATE CASCADE,
    FOREIGN KEY (customer_id)  REFERENCES customer(customer_id)   ON UPDATE CASCADE,
    FOREIGN KEY (staff_id)     REFERENCES staff(staff_id)         ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS payment (
    payment_id   SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    customer_id  SMALLINT UNSIGNED NOT NULL,
    staff_id     TINYINT UNSIGNED  NOT NULL,
    rental_id    INT               NOT NULL,
    amount       DECIMAL(5,2)      NOT NULL,
    payment_date DATETIME          NOT NULL,
    last_update  TIMESTAMP         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (payment_id),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id) ON UPDATE CASCADE,
    FOREIGN KEY (staff_id)    REFERENCES staff(staff_id)       ON UPDATE CASCADE,
    FOREIGN KEY (rental_id)   REFERENCES rental(rental_id)     ON UPDATE CASCADE
);


--  SHADOW TABLES (_log)
--  Capturan cada cambio en las tablas OUT para el Sync-OUT.


CREATE TABLE IF NOT EXISTS customer_log (
    log_id       INT          NOT NULL AUTO_INCREMENT,
    operation    CHAR(1)      NOT NULL COMMENT 'I=Insert, U=Update, D=Delete',
    log_datetime DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Snapshot de la fila afectada
    customer_id  SMALLINT UNSIGNED,
    store_id     TINYINT UNSIGNED,
    first_name   VARCHAR(45),
    last_name    VARCHAR(45),
    email        VARCHAR(50),
    address_id   SMALLINT UNSIGNED,
    active       TINYINT(1),
    create_date  DATETIME,
    last_update  TIMESTAMP    NULL,

    PRIMARY KEY (log_id)
);

CREATE TABLE IF NOT EXISTS rental_log (
    log_id       INT                NOT NULL AUTO_INCREMENT,
    operation    CHAR(1)            NOT NULL COMMENT 'I=Insert, U=Update, D=Delete',
    log_datetime DATETIME           NOT NULL DEFAULT CURRENT_TIMESTAMP,

    rental_id    INT,
    rental_date  DATETIME,
    inventory_id MEDIUMINT UNSIGNED,
    customer_id  SMALLINT UNSIGNED,
    return_date  DATETIME,
    staff_id     TINYINT UNSIGNED,
    last_update  TIMESTAMP          NULL,

    PRIMARY KEY (log_id)
);

CREATE TABLE IF NOT EXISTS payment_log (
    log_id       INT               NOT NULL AUTO_INCREMENT,
    operation    CHAR(1)           NOT NULL COMMENT 'I=Insert, U=Update, D=Delete',
    log_datetime DATETIME          NOT NULL DEFAULT CURRENT_TIMESTAMP,

    payment_id   SMALLINT UNSIGNED,
    customer_id  SMALLINT UNSIGNED,
    staff_id     TINYINT UNSIGNED,
    rental_id    INT,
    amount       DECIMAL(5,2),
    payment_date DATETIME,
    last_update  TIMESTAMP         NULL,

    PRIMARY KEY (log_id)
);


--  TABLA DE CONTROL DE SINCRONIZACIÓN
--  Registra cuándo se hizo cada sync y su resultado.


CREATE TABLE IF NOT EXISTS sync_log (
    sync_id      INT          NOT NULL AUTO_INCREMENT,
    sync_type    VARCHAR(10)  NOT NULL COMMENT 'IN o OUT',
    sync_datetime DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status       VARCHAR(10)  NOT NULL COMMENT 'OK o ERROR',
    message      TEXT,
    rows_affected INT         DEFAULT 0,
    PRIMARY KEY (sync_id)
);


--  TRIGGERS pa customer


DELIMITER $$

CREATE TRIGGER trg_customer_insert
AFTER INSERT ON customer
FOR EACH ROW
BEGIN
    INSERT INTO customer_log (
        operation, customer_id, store_id, first_name, last_name,
        email, address_id, active, create_date, last_update
    ) VALUES (
        'I', NEW.customer_id, NEW.store_id, NEW.first_name, NEW.last_name,
        NEW.email, NEW.address_id, NEW.active, NEW.create_date, NEW.last_update
    );
END$$

CREATE TRIGGER trg_customer_update
AFTER UPDATE ON customer
FOR EACH ROW
BEGIN
    INSERT INTO customer_log (
        operation, customer_id, store_id, first_name, last_name,
        email, address_id, active, create_date, last_update
    ) VALUES (
        'U', NEW.customer_id, NEW.store_id, NEW.first_name, NEW.last_name,
        NEW.email, NEW.address_id, NEW.active, NEW.create_date, NEW.last_update
    );
END$$

CREATE TRIGGER trg_customer_delete
AFTER DELETE ON customer
FOR EACH ROW
BEGIN
    INSERT INTO customer_log (
        operation, customer_id, store_id, first_name, last_name,
        email, address_id, active, create_date, last_update
    ) VALUES (
        'D', OLD.customer_id, OLD.store_id, OLD.first_name, OLD.last_name,
        OLD.email, OLD.address_id, OLD.active, OLD.create_date, OLD.last_update
    );
END$$


--  TRIGGERS - rental


CREATE TRIGGER trg_rental_insert
AFTER INSERT ON rental
FOR EACH ROW
BEGIN
    INSERT INTO rental_log (
        operation, rental_id, rental_date, inventory_id,
        customer_id, return_date, staff_id, last_update
    ) VALUES (
        'I', NEW.rental_id, NEW.rental_date, NEW.inventory_id,
        NEW.customer_id, NEW.return_date, NEW.staff_id, NEW.last_update
    );
END$$

CREATE TRIGGER trg_rental_update
AFTER UPDATE ON rental
FOR EACH ROW
BEGIN
    INSERT INTO rental_log (
        operation, rental_id, rental_date, inventory_id,
        customer_id, return_date, staff_id, last_update
    ) VALUES (
        'U', NEW.rental_id, NEW.rental_date, NEW.inventory_id,
        NEW.customer_id, NEW.return_date, NEW.staff_id, NEW.last_update
    );
END$$

CREATE TRIGGER trg_rental_delete
AFTER DELETE ON rental
FOR EACH ROW
BEGIN
    INSERT INTO rental_log (
        operation, rental_id, rental_date, inventory_id,
        customer_id, return_date, staff_id, last_update
    ) VALUES (
        'D', OLD.rental_id, OLD.rental_date, OLD.inventory_id,
        OLD.customer_id, OLD.return_date, OLD.staff_id, OLD.last_update
    );
END$$


--  TRIGGERS - payment


CREATE TRIGGER trg_payment_insert
AFTER INSERT ON payment
FOR EACH ROW
BEGIN
    INSERT INTO payment_log (
        operation, payment_id, customer_id, staff_id,
        rental_id, amount, payment_date, last_update
    ) VALUES (
        'I', NEW.payment_id, NEW.customer_id, NEW.staff_id,
        NEW.rental_id, NEW.amount, NEW.payment_date, NEW.last_update
    );
END$$

CREATE TRIGGER trg_payment_update
AFTER UPDATE ON payment
FOR EACH ROW
BEGIN
    INSERT INTO payment_log (
        operation, payment_id, customer_id, staff_id,
        rental_id, amount, payment_date, last_update
    ) VALUES (
        'U', NEW.payment_id, NEW.customer_id, NEW.staff_id,
        NEW.rental_id, NEW.amount, NEW.payment_date, NEW.last_update
    );
END$$

CREATE TRIGGER trg_payment_delete
AFTER DELETE ON payment
FOR EACH ROW
BEGIN
    INSERT INTO payment_log (
        operation, payment_id, customer_id, staff_id,
        rental_id, amount, payment_date, last_update
    ) VALUES (
        'D', OLD.payment_id, OLD.customer_id, OLD.staff_id,
        OLD.rental_id, OLD.amount, OLD.payment_date, OLD.last_update
    );
END$$

DELIMITER ;
