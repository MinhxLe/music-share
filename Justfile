make_migration migration_name:
  alembic revision --autogenerate -m {{migration_name}}
