import os
import requests
import json

COUNTRIES_API_URL = "https://restcountries.com/v3.1/all"
FLAGS_BASE_URL = "https://restcountries.com/data"

def download_flags():
    response = requests.get(COUNTRIES_API_URL)
    countries_data = response.json()
    arr = []
    for country_data in countries_data:
        # print(country_data['flags']['png'])
        # response = requests.get(country_data['flags']['png'])
        # with open("./images/flags/" + str(country_data['cca2']).lower() + ".png", 'wb') as file:
        #     file.write(response.content)

        try:
            output = extract_info(country_data)
            arr.append({"data": output})
        except Exception as e:
            print(f"Ошибка при обработке данных для страны: {country_data.get('name', {}).get('common', 'Неизвестно')}")
            print(str(e))

    with open("./country.json", "w") as f:
        f.write(json.dumps(arr, indent=2))

def extract_info(data):
    # Извлекаем общее имя страны на английском
    common_name = data.get('name', {}).get('common', 'Unknown')
    
    # Извлекаем все переводы имен стран/
    translations = [{"lang": lang, "name": trans_data['common']} for lang, trans_data in data['translations'].items()]

    # Добавляем английскую версию
    translations.insert(0, {"lang": "eng", "name": common_name})

    # Извлекаем код страны
    country_code = data['cca2']

    # Извлекаем номер страны
    phone_number_root = data['idd'].get('root', '')  # Замените 'root' на значение по умолчанию, если оно отсутствует
    phone_number_suffix = data['idd'].get('suffixes', [''])[0]  # Замените 'suffixes' на список с пустой строкой, если он отсутствует
    phone_number = phone_number_root + phone_number_suffix

    # Извлекаем временную зону
    timezone = data['timezones'][0]

    result = {
        "name_country": translations,
        "code": country_code,
        "number": phone_number,
        "timezone": timezone
    }

    return result

if __name__ == "__main__":
    download_flags()
