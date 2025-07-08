"""
Conftest module for configuring pytest asynchronous MongoDB tests.

This module sets up an asynchronous test environment for MongoDB-based tests using
pytest-asyncio. It includes configurations for:
    1. A session-scoped event loop to maintain consistency across async tests.
    2. Connecting to MongoDB and retrieving a client instance.
    3. Providing access to the test database.
    4. Cleaning the test database once per session to avoid cross-test contamination.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from cryptomesh.db import connect_to_mongo, close_mongo_connection, get_client,get_database
from httpx import AsyncClient, ASGITransport
from cryptomesh.server import app

TEST_DB = os.environ.get("MONGO_DATABASE_NAME","cryptomesh_test")
# ───────────────────────────────
# Session‑scoped Event Loop
# ───────────────────────────────
@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """
    Create a session-scoped event loop for all tests.

    This fixture provides a single event loop for the entire test session,
    ensuring consistent asynchronous behavior across tests. The loop is created
    at the beginning of the session and closed after all tests have completed.
    
    Yields:
        asyncio.AbstractEventLoop: The created event loop.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ───────────────────────────────
# MongoDB Connection and Client Retrieval
# ───────────────────────────────
@pytest_asyncio.fixture(scope="session",autouse=True)
async def connect_and_get_client(event_loop):
    """
    Connect to MongoDB and yield the client instance.

    This session-scoped fixture connects to MongoDB using the MONGO_URI,
    yields the MongoDB client for use in tests, and ensures that the connection
    is properly closed after the tests have run.
    
    Args:
        event_loop (asyncio.AbstractEventLoop): The session-scoped event loop.
    
    Yields:
        MongoClient: The connected MongoDB client instance.
    """
    await connect_to_mongo()
    yield get_client()
    await close_mongo_connection()


# ───────────────────────────────
#  Database Access Fixture
# ───────────────────────────────
@pytest_asyncio.fixture
async def get_db(connect_and_get_client):
    """
    Provide access to the test database.

    This fixture retrieves and returns the test database instance using the
    connected MongoDB client provided by the 'connect_and_get_client' fixture.
    
    Args:
        connect_and_get_client: The connected MongoDB client.
    
    Returns:
        Database: The database instance specified by the TEST_DB name.
    """
    return get_database()


# ───────────────────────────────
# Clean Database Once per Session
# ───────────────────────────────
@pytest_asyncio.fixture(scope="session", autouse=True)
async def clean_db(connect_and_get_client):
    """
    Clean the test database once per session.

    This fixture ensures that the test database is clean at the start of the test
    session by dropping the database. This cleanup operation helps avoid side effects
    between tests.
    
    Args:
        connect_and_get_client: The connected MongoDB client.
    
    Yields:
        None: No value is returned; the purpose is to perform database cleanup.
    """
    await connect_and_get_client.drop_database(TEST_DB)
    yield

@pytest_asyncio.fixture()
async def client(event_loop):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://localhost") as ac:
        yield ac