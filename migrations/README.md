# Database migrations

Python migrations are applied in filename order by:

```bash
python3 -m scripts.apply_migrations
```

Migrations inspect existing indexes and constraints before applying each operation, so an interrupted migration can be rerun safely. Before applying a migration to an existing database, take a backup and resolve duplicate ticket numbers, invalid scores, or multiple ongoing semesters. A migration intentionally fails instead of silently discarding conflicting data.
