-- releases-app canonical dump (GH-32 grammar: GID-keyed rows, natural keys elsewhere,
-- no integer PKs/FKs as values; rebuild renumbers deterministically)
-- generation: 1
-- table: schema_migrations
INSERT INTO schema_migrations(version, applied_at) VALUES('1', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('2', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('3', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('4', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('5', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('6', '2026-08-28T16:49:25Z');
-- table: settings
INSERT INTO settings(key, value) VALUES('enforcement', 'lenient');
INSERT INTO settings(key, value) VALUES('generation', '1');
INSERT INTO settings(key, value) VALUES('repo_slug', 'XYZ-code-intelligence');
-- table: repos
INSERT INTO repos(global_id, slug) VALUES('repo-01M14MDD681EQCR3FG723G8CJ9', 'XYZ-code-intelligence');
