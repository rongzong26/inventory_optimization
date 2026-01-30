-- Grant permissions explicitly to rong.zong@databricks.com
-- This ensures the endpoint (which may run as this user) has access

-- Grant catalog access
GRANT USAGE ON CATALOG `rz-demo-mining` TO `rong.zong@databricks.com`;

-- Grant schema access
GRANT USAGE ON SCHEMA `rz-demo-mining`.`supply-chain` TO `rong.zong@databricks.com`;

-- Grant table access
GRANT SELECT ON TABLE `rz-demo-mining`.`supply-chain`.`gold_master_part_inventory` TO `rong.zong@databricks.com`;

-- Verify grants
SHOW GRANTS ON TABLE `rz-demo-mining`.`supply-chain`.`gold_master_part_inventory`;
