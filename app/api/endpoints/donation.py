from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.models import CharityProject, User
from app.schemas.donation import DonationBase, DonationCreate, DonationDB
from app.services.investing import investing_process

router = APIRouter()


@router.post('/',
             response_model=DonationCreate,
             response_model_exclude_none=True
             )
async def create_donation(donation: DonationBase,
                          session: AsyncSession = Depends(get_async_session),
                          user: User = Depends(current_user)
                          ):
    """Сделать пожертвование."""
    new_donation = await donation_crud.create(donation, session, user)
    await investing_process(new_donation, CharityProject, session)

    return new_donation


@router.get(
    '/my',
    response_model=list[DonationCreate],
    response_model_exclude={'user_id'},
)
async def get_user_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Вернуть список пожертвований пользователя, выполняющего запрос."""
    donations = await donation_crud.get_by_user(
        session=session, user=user
    )
    return donations


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    """Только для суперюзеров.

    Возвращает список всех пожертвований.
    """
    all_donations = await donation_crud.get_multi(session)
    return all_donations
