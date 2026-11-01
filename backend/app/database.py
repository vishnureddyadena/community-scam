import os
import ssl
import urllib.parse
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.models import Base, Area, VerifiedIdentifier
from app.data.areas import SEED_AREAS
from app.data.verified import SEED_VERIFIED_IDENTIFIERS

raw_url = settings.DATABASE_URL or os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///scamradar.db")

# Normalize Postgres / Supabase / Neon / Render connection strings
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("sqlite://") and not raw_url.startswith("sqlite+aiosqlite://"):
    raw_url = raw_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

connect_args = {}
engine_kwargs = {
    "echo": False,
    "future": True,
}

if raw_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    db_url = raw_url
else:
    # Handle cloud PostgreSQL (Supabase, Neon, Render, Railway, AWS RDS)
    # Strip query parameters that asyncpg rejects (e.g. ?sslmode=require)
    u = urllib.parse.urlsplit(raw_url)
    qs = urllib.parse.parse_qs(u.query)
    sslmode = qs.pop("sslmode", None)
    clean_query = urllib.parse.urlencode(qs, doseq=True)
    db_url = urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, clean_query, u.fragment))

    # Enable SSL for cloud databases or if sslmode was specified
    is_cloud_db = any(domain in db_url.lower() for domain in ["supabase", "neon.tech", "render.com", "railway.app", "rds.amazonaws.com"])
    if sslmode or is_cloud_db:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ctx

    # Add resilient connection pooling options for cloud postgres
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

engine_kwargs["connect_args"] = connect_args

try:
    engine = create_async_engine(db_url, **engine_kwargs)
except Exception as e:
    # Safe fallback to local SQLite if remote connection string parsing fails
    print(f"[WARN] Failed to configure database engine for {db_url}: {e}. Falling back to SQLite.")
    db_url = "sqlite+aiosqlite:///scamradar.db"
    engine = create_async_engine(db_url, connect_args={"check_same_thread": False}, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"[WARN] Database schema creation notice: {e}")

    # Seed initial areas and verified identifiers if not present
    try:
        async with AsyncSessionLocal() as session:
            # Check areas
            res = await session.execute(select(Area).limit(1))
            if not res.scalars().first():
                for area_data in SEED_AREAS:
                    area = Area(**area_data)
                    session.add(area)
                await session.commit()

            # Check verified identifiers
            res_v = await session.execute(select(VerifiedIdentifier).limit(1))
            if not res_v.scalars().first():
                for v_data in SEED_VERIFIED_IDENTIFIERS:
                    vi = VerifiedIdentifier(**v_data)
                    session.add(vi)
                await session.commit()
    except Exception as e:
        print(f"[WARN] Database seeding notice: {e}")
