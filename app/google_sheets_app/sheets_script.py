import gspread
import os

# --- Настройка доступа к Google Sheets ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "server_account.json")  # путь к JSON-ключу
SHEET_NAME = "house_log_api" # имя таблицы

def write_row_sheets(house_info:list, service_account_json:str=SERVICE_ACCOUNT_FILE, sheet_name:str=SHEET_NAME)->str:
    """
    Записываем стрчку с данными в google sheets
    :param house_info: лист с данными конкретного объекта
    :param service_account_json: путь до файла с данными от сервисного аккаунта
    :param sheet_name: название таблицы
    :return: статус - объект успешно записан в таблицу/объект не записан: error
    """
    try:
        gc = gspread.service_account(filename=service_account_json)
        sheet = gc.open(sheet_name).sheet1
        sheet.append_row(house_info, value_input_option='USER_ENTERED')
        return 'Объект успешно записан в таблицу'
    except Exception as e:
        return f'Объект не записан: {e}'

def get_columns_sheets(service_account_json:str=SERVICE_ACCOUNT_FILE, sheet_name:str=SHEET_NAME)->list:
    try:
        gc = gspread.service_account(filename=service_account_json)
        sheet = gc.open(sheet_name).sheet1
        col_values = sheet.col_values(1)
    except Exception as e:
        return f'Объект не найден: {e}'
    return col_values

if __name__=="__main__":
    print(get_columns_sheets())


