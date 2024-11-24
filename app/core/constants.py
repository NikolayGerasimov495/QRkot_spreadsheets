from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"
ROW_COUNT = 100
COLUMN_COUNT = 11
SPREADSHEET_TITLE_TEMPLATE = 'Отчёт от {}'
SPREADSHEET_LOCALE = 'ru_RU'
DEFAULT_SHEET_PROPERTIES = {
    'sheetType': 'GRID',
    'sheetId': 0,
    'title': 'Лист1',
    'gridProperties': {
        'rowCount': ROW_COUNT,
        'columnCount': COLUMN_COUNT
    }
}
PERMISSIONS_BODY_TEMPLATE = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email
}
UPDATE_BODY_TEMPLATE = {
    'majorDimension': 'ROWS',
    'values': []
}
TABLE_HEADER = [
    ['Отчёт от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
UPDATERANGE = 'A1:E30'
VALUE_INPUT_OPTION = 'USER_ENTERED'
