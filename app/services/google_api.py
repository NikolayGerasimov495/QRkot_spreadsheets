from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.core.constants import (DEFAULT_SHEET_PROPERTIES, FORMAT,
                                PERMISSIONS_BODY_TEMPLATE, SPREADSHEET_LOCALE,
                                SPREADSHEET_TITLE_TEMPLATE, TABLE_HEADER,
                                UPDATE_BODY_TEMPLATE, UPDATERANGE,
                                VALUE_INPUT_OPTION)


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    now_date_time = datetime.now().strftime(FORMAT)

    service = await wrapper_services.discover('sheets', 'v4')

    spreadsheet_body = {
        'properties': {
            'title': SPREADSHEET_TITLE_TEMPLATE.format(now_date_time),
            'locale': SPREADSHEET_LOCALE
        },
        'sheets': [DEFAULT_SHEET_PROPERTIES]
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(spreadsheetid: str,
                               wrapper_services: Aiogoogle) -> None:
    permissions_body = PERMISSIONS_BODY_TEMPLATE.copy()
    permissions_body['emailAddress'] = settings.email

    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        )
    )


async def spreadsheets_update_value(spreadsheet_id: str,
                                    projects: list,
                                    wrapper_services: Aiogoogle) -> None:
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    TABLE_HEADER[0][1] = now_date_time

    table_values = TABLE_HEADER + [
        [str(project['name']), str(project['delta']),
         str(project['description'])] for project in projects
    ]

    update_body = UPDATE_BODY_TEMPLATE.copy()
    update_body['values'] = table_values

    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=UPDATERANGE,
            valueInputOption=VALUE_INPUT_OPTION,
            json=update_body
        )
    )
