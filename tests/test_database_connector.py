import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from src.settings import settings
from src.database_connector import AsyncDatabase  # replace with actual module name

@pytest.fixture
def async_database():
    with patch.object(settings, 'database_uri', return_value='sqlite:///test.db'), \
         patch('AsyncDatabase.create_async_engine', new_callable=AsyncMock), \
         patch('AsyncDatabase.sessionmaker', new_callable=AsyncMock):  # replace with actual module name
        yield AsyncDatabase()

@pytest.mark.asyncio
async def test_create_tables(async_database):
    with patch.object(AsyncDatabase, 'engine', new_callable=AsyncMock) as mock_engine:
        mock_conn = MagicMock()
        mock_conn.run_sync = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn

        await async_database.create_tables()

        mock_conn.run_sync.assert_called_once()

@pytest.mark.asyncio
async def test_get_db_session(async_database):
    with patch.object(AsyncDatabase, 'sessionmaker', new_callable=AsyncMock) as mock_sessionmaker:
        mock_db_session = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.close = AsyncMock()
        mock_sessionmaker.return_value = mock_db_session

        async with async_database.get_db_session() as session:
            pass

        mock_db_session.commit.assert_called_once()
        mock_db_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_get_db_session_exception(async_database):
    with patch.object(AsyncDatabase, 'sessionmaker', new_callable=AsyncMock) as mock_sessionmaker:
        mock_db_session = MagicMock()
        mock_db_session.commit = AsyncMock()
        mock_db_session.close = AsyncMock()
        mock_sessionmaker.return_value = mock_db_session

        with pytest.raises(SQLAlchemyError):
            async with async_database.get_db_session() as session:
                raise SQLAlchemyError('test exception')

        mock_db_session.commit.assert_not_called()
        mock_db_session.close.assert_called_once()
