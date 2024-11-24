from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User


class CRUDDonation(CRUDBase):

    async def get_by_user(self,
                          user: User,
                          session: AsyncSession
                          ):
        donations = await session.execute(
            select(Donation).where(Donation.user_id == user.id)
        )
        return donations.scalars().all()

    async def get_free_donations(self, session: AsyncSession):
        result = await session.execute(
            select(Donation).where(Donation.id.is_(None))
        )
        return result.scalars().all()


donation_crud = CRUDDonation(Donation)
