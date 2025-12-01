-- ===== Craft local scrub =====
-- Clear sessions, tokens, and queue jobs
TRUNCATE TABLE sessions;
TRUNCATE TABLE tokens;
TRUNCATE TABLE queue;

-- Mass-update non-admin emails to a safe domain (keeps logins unique):
UPDATE users
SET email = CONCAT('local+', id, '@example.invalid')
WHERE admin = 0;

-- OPTIONAL: set a known email for a primary admin (pick the right id!)
-- UPDATE users SET email='you@yourdomain.test' WHERE id=1;

-- OPTIONAL: disable any pending user activations
UPDATE users SET pending = 0 WHERE pending = 1;

-- OPTIONAL: if contact-form/other plugins store addresses in settings tables,
-- they can be replaced similarly; this varies by plugin.
-- Example pattern to find likely secrets:
-- SELECT TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
--  WHERE TABLE_SCHEMA = DATABASE()
--    AND COLUMN_NAME REGEXP '(api|key|secret|token|smtp|password)';
