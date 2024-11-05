-- Lab 3
-- rxlei
-- Oct 16, 2024

USE `rxlei`;
-- BAKERY-1
-- Using a single SQL statement, reduce the prices of Lemon Cake and Napoleon Cake by $2.
UPDATE goods 
SET Price = Price - 2 
WHERE GId IN ('20-BC-L-10', '46-11');


USE `rxlei`;
-- BAKERY-2
-- Using a single SQL statement, increase by 15% the price of all Apricot or Chocolate flavored items with a current price below $5.95.
UPDATE goods 
SET Price = Price * 1.15 
WHERE (Flavor = 'Apricot' OR Flavor = 'Chocolate') AND Price < 5.95;


USE `rxlei`;
-- BAKERY-3
-- Add the capability for the database to record payment information for each receipt in a new table named payments (see assignment PDF for task details)
CREATE TABLE payments(
    Receipt int NOT NULL,
    Amount decimal(19,2) NOT NULL,
    PaymentSettled DATETIME NOT NULL,
    PaymentType varchar(20) NOT NULL ,
    FOREIGN KEY reciept_fk (Receipt) REFERENCES receipts(RNumber),
    PRIMARY KEY (Receipt, Amount)
);


USE `rxlei`;
-- BAKERY-4
-- Create a database trigger to prevent the sale of Meringues (any flavor) and all Almond-flavored items on Saturdays and Sundays.
CREATE TRIGGER sunday_sales_check BEFORE INSERT on items
FOR EACH ROW
    BEGIN
        DECLARE type_of_item_sold varchar(100);
        DECLARE flavor_of_item_sold varchar(100);
        DECLARE date_of_sale DATE;
        SELECT Food INTO type_of_item_sold FROM goods WHERE GId = NEW.Item;
        SELECT Flavor INTO flavor_of_item_sold FROM goods WHERE GId = NEW.Item;
        SELECT SaleDate INTO date_of_sale FROM receipts WHERE RNumber = NEW.Receipt;
        
        IF ((DAYOFWEEK(date_of_sale) = 1 OR DAYOFWEEK(date_of_sale) = 7) AND (type_of_item_sold = 'Meringue' OR flavor_of_item_sold = 'Almond')) then
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot sell this item on sundays';
        
        END IF;
    END;


USE `rxlei`;
-- AIRLINES-1
-- Enforce the constraint that flights should never have the same airport as both source and destination (see assignment PDF)
CREATE TRIGGER source_destination_check BEFORE INSERT on flights
FOR EACH ROW
    BEGIN
        if (NEW.SourceAirport = NEW.DestAirport) then
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Source and Destination Airport Must not be the same';
        END IF;
    END;


USE `rxlei`;
-- AIRLINES-2
-- Add a "Partner" column to the airlines table to indicate optional corporate partnerships between airline companies (see assignment PDF)
-- ALTER TABLE airlines
-- ADD Partner VARCHAR(50);

-- ALTER TABLE airlines
-- ADD CONSTRAINT fk_partner_abbreviation
-- FOREIGN KEY (Partner) REFERENCES airlines(Abbreviation);

-- ALTER TABLE airlines
-- ADD CONSTRAINT chk_no_self_partnership
-- CHECK (Partner IS NULL OR Partner <> Abbreviation);

-- ALTER TABLE airlines
-- ADD CONSTRAINT uq_partner UNIQUE (Partner);

SELECT Abbreviation FROM airlines WHERE Airline = 'JetBlue Airways';
-- Expected result: 'JetBlue'

SELECT Abbreviation FROM airlines WHERE Airline = 'Southwest Airlines';
-- Expected result: 'Southwest'

UPDATE airlines
SET Partner = 'Southwest'
WHERE Abbreviation = 'JetBlue';

UPDATE airlines
SET Partner = 'JetBlue'
WHERE Abbreviation = 'Southwest';

UPDATE airlines
SET Partner = 'JetBlue'
WHERE Abbreviation = 'Frontier';


USE `rxlei`;
-- KATZENJAMMER-1
-- Change the name of two instruments: 'bass balalaika' should become 'awesome bass balalaika', and 'guitar' should become 'acoustic guitar'. This will require several steps. You may need to change the length of the instrument name field to avoid data truncation. Make this change using a schema modification command, rather than a full DROP/CREATE of the table.
ALTER TABLE Instruments MODIFY Instrument VARCHAR(150); -- Adjust column length

UPDATE Instruments 
SET Instrument = 'awesome bass balalaika' 
WHERE Instrument = 'bass balalaika';

UPDATE Instruments 
SET Instrument = 'acoustic guitar' 
WHERE Instrument = 'guitar';


USE `rxlei`;
-- KATZENJAMMER-2
-- Keep in the Vocals table only those rows where Solveig (id 1 -- you may use this numeric value directly) sang, but did not sing lead.
DELETE FROM Vocals
WHERE Bandmate != 1 OR `Type` = 'lead';


