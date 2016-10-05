import logging
import pytest

from . import db
from ... import utils

logger = logging.getLogger(__name__)


@pytest.fixture
@pytest.mark.asyncio
def open_db(event_loop):
    class AsyncDBConnection:
        def __init__(self):
            self.db_interface = db.MongodbInterface(uri='mongo', db_name='test')

        async def __aenter__(self):
            await self.db_interface.connect(loop=event_loop)
            return self.db_interface

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            self.db_interface = None

    return AsyncDBConnection


@pytest.mark.asyncio
async def test_store_restore_user(open_db):
    async with open_db() as db_interface:
        user = utils.build_fake_user()

        user_id = await db_interface.set_user(user._response)
        restored_user = await db_interface.get_user(user_id)

        assert user.items() == restored_user.items()


@pytest.mark.asyncio
async def test_store_restore_session(open_db):
    async with open_db() as db_interface:
        session = utils.build_fake_session()
        user_id = '123456789'

        session_id = await db_interface.set_session(user_id, session._response)
        logger.debug('session_id')
        logger.debug(session_id)
        restored_session = await db_interface.get_session(session_id=session_id)
        logger.debug('restored_session')
        logger.debug(restored_session)
        restored_session = await db_interface.get_session(user_id=user_id)

        assert list(session.items()) == [(key, value) for (key, value) in restored_session.items() if
                                         key not in ['_id']]
