-- releases-app canonical dump (GH-32 grammar: GID-keyed rows, natural keys elsewhere,
-- no integer PKs/FKs as values; rebuild renumbers deterministically)
-- generation: 2
-- table: schema_migrations
INSERT INTO schema_migrations(version, applied_at) VALUES('1', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('2', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('3', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('4', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('5', '2026-08-28T16:49:25Z');
INSERT INTO schema_migrations(version, applied_at) VALUES('6', '2026-08-28T16:49:25Z');
-- table: settings
INSERT INTO settings(key, value) VALUES('enforcement', 'lenient');
INSERT INTO settings(key, value) VALUES('generation', '2');
INSERT INTO settings(key, value) VALUES('repo_slug', 'XYZ-code-intelligence');
-- table: repos
INSERT INTO repos(global_id, slug) VALUES('repo-01M14MDD681EQCR3FG723G8CJ9', 'XYZ-code-intelligence');
-- table: roadmap_items
INSERT INTO roadmap_items(global_id, repo_gid, gh_number, title, section, position, status_marker, complexity, risk, effort, doc_path, issue_url, raw_text, first_seen, updated_at, rating_pri, rating_sev, rating_appeal, rating_effort, rating_ovr) VALUES('rmi-01M15YR2N9JQ8GY8S3F4SNXBRH', 'repo-01M14MDD681EQCR3FG723G8CJ9', '5', 'Experiment: int8 quantization (ONNX / OpenVINO) for query-encode latency', 'Queue / parked intake', '1', '🆕', NULL, NULL, NULL, 'PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md', 'https://github.com/HiQS-Labs/XYZ-code-intelligence/issues/5', '- **GH-5 · int8 Quantization Benchmark on GCP Intel** — [PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md](<PROJECT/2-WORKING/v0.5/GH-5-QUANTIZATION-BENCHMARK.md>) — benchmark ONNX/OpenVINO int8 query-encode latency on Sapphire Rapids; rated 3/3/3/5', '2026-08-29T05:09:15Z', '2026-08-29T05:09:15Z', '3', '3', '3', '5', NULL);
-- table: op_receipts
INSERT INTO op_receipts(op, target_gid, at, txn_id, session_id, state_digest_before, state_digest_after) VALUES('roadmap-add', 'rmi-01M15YR2N9JQ8GY8S3F4SNXBRH', '2026-08-29T05:09:15Z', '62b99ccbc3dd418b9ec3a0b6a4c6a8a1', 'default', '16ffc3310565b1d2b26be2311dc66ad148b233f0af1a1288ff789a456c29b1d8', 'cf6c0b08e995d816477b84ff80ba01cbb0feea90c39932f3179e9f4046ccf84f');
