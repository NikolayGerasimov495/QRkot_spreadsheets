from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def update_donation(donation: Donation, amount: int):
    donation.invested_amount += amount
    if donation.invested_amount >= donation.full_amount:
        donation.fully_invested = True
        donation.close_date = datetime.utcnow()


async def investing_process(
        charity_project: CharityProject,
        donation_model: Donation,
        session: AsyncSession,
) -> CharityProject:
    result = await session.execute(
        select(donation_model).
        where(donation_model.fully_invested.is_(False)).
        order_by(donation_model.create_date)
    )
    available_donations = result.scalars().all()

    for donation in available_donations:
        free_amount_in_project = (charity_project.full_amount -
                                  charity_project.invested_amount)
        free_amount_in_donation = (donation.full_amount -
                                   donation.invested_amount)

        if free_amount_in_project > free_amount_in_donation:
            charity_project.invested_amount += free_amount_in_donation
            await update_donation(donation, donation.full_amount)

        elif free_amount_in_project == free_amount_in_donation:
            charity_project.invested_amount += free_amount_in_project
            charity_project.fully_invested = True
            charity_project.close_date = datetime.utcnow()
            await update_donation(donation, donation.full_amount)

        else:
            charity_project.invested_amount = charity_project.full_amount
            charity_project.fully_invested = True
            charity_project.close_date = datetime.utcnow()
            await update_donation(donation, free_amount_in_project)

        session.add(charity_project)
        session.add(donation)

    await session.commit()
    await session.refresh(charity_project)
    return charity_project
