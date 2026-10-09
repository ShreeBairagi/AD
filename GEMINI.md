# Gemini AI Assistant Rules

Follow these rules for all code generation and modifications in this repository:

1. **Keep code simple:** Use short functions, no classes unless strictly needed, no ORMs, and no extra libraries without asking first.
2. **Simple queries only:**
   - Use raw SQL with `psycopg2` for PostgreSQL.
   - Use plain `pymongo` calls for MongoDB.
   - No CTEs, window functions, subqueries, or aggregation pipelines.
   - Each query must be under 8 lines.
   - Add a one-line plain-English comment above each query.
3. **Centralized database queries:** Put every query in one file per database: `db/postgres_queries.py` and `db/mongo_queries.py`.
4. **Dependencies and Safety:**
   - Always pin dependency versions.
   - Never run destructive commands without asking for permission first.
5. **File explanation:** After creating files, explain each in one line.
