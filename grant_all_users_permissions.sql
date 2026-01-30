-- Grant table permissions to ALL account users
-- This covers any service principal that the endpoint might use

-- Catalog and schema access
GRANT USE CATALOG ON CATALOG `rz-demo-mining` TO `account users`;
GRANT USE SCHEMA ON SCHEMA `rz-demo-mining`.`supply-chain` TO `account users`;

-- Table access
GRANT SELECT ON TABLE `rz-demo-mining`.`supply-chain`.`gold_master_part_inventory` TO `account users`;

-- Verify permissions
SHOW GRANTS ON CATALOG `rz-demo-mining`;
SHOW GRANTS ON SCHEMA `rz-demo-mining`.`supply-chain`;
SHOW GRANTS ON TABLE `rz-demo-mining`.`supply-chain`.`gold_master_part_inventory`;
