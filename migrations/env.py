"""Alembic environment for the single consolidated BSS-Core database.

Imports the ORM metadata of every business module so autogenerate and
``upgrade head`` cover the complete schema (constitution Section 7).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

from src.domain.database import SQLALCHEMY_DATABASE_URL
from src.models.billing_management.infrastructure.orm import Base as BillingBase
from src.models.customer_management.infrastructure.orm import Base as CustomerBase
from src.models.dashboard_metric import Base as DashboardMetricBase
from src.models.order_management.infrastructure.orm import Base as OrderBase
from src.models.reporting_period import Base as ReportingPeriodBase
from src.models.shipment_management.infrastructure.orm import Base as ShipmentBase

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Use the application's configured database URL for migrations.
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support — every module's ORM metadata.
target_metadata: list[MetaData] = [
    CustomerBase.metadata,
    OrderBase.metadata,
    ShipmentBase.metadata,
    BillingBase.metadata,
    DashboardMetricBase.metadata,
    ReportingPeriodBase.metadata,
]


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
