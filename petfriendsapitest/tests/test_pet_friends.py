from api import PetFriends
from settings import valid_email, valid_password
import pytest
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='миньон', animal_type='шериф', age='8', pet_photo='images/Minion.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Вася", "кот", "2", "images/cat.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='сибирская', age=3):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_add_new_pet_without_photo_with_valid_data(name='плато', animal_type='дог', age=4):
    """Проверяем что можно добавить питомца с корректными данными без фото"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] == ""


def test_successful_add_photo_pet_with_valid_data(pet_photo='images/dog.jpg'):
    """Проверяем возможность добовления фото  питомца, поддерживаемый формат JPG, JPEG or PNG"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем добавить его фото
    if len(my_pets['pets']) > 0:
        status, result = pf.set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        # Проверяем что статус ответа = 200 и фото питомца соответствует заданному
        assert status == 200
        assert result['pet_photo'] != ""
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_no_get_api_key_for_no_valid_user_po_email(email='zen@ma.ru', password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 при неправельном вводе емейл но правельном
    пароле и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_no_get_api_key_for_no_valid_user_po_parol(email=valid_email, password='12345'):
    """ Проверяем что запрос api ключа возвращает статус 403 при неправельном вводе пароле но правельном
    email и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_no_get_api_key_for_no_valid_user_po_pustoy(email='', password=''):
    """ Проверяем что запрос api ключа возвращает статус 403 при пустом пароле и пустом
    email и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    assert 'key' not in result


def test_no_get_all_pets_with_no_valid_key_pustoy(filter=''):
    """ Проверяем что запрос всех питомцев возвращает  ошибку 403.
    Для этого сначала создадаим пучтой api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что выдается ошибка .
    Доступное значение параметра filter - 'my_pets' либо '' """

    auth_key = {'key': ''}
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403


def test_no_get_all_pets_with_no_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает  ошибку 403.
    Для этого сначала создадаим сгенирированый случайным образом api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что выдается ошибка .
    Доступное значение параметра filter - 'my_pets' либо '' """

    auth_key = {'key': 'ea738148a1f19838e2c5d1413887f3691a3731380e733e877b0ae720'}
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403


def test_no_get_all_pets_with_valid_key_and_not_valid_filter(filter='other_pets'):
    """ Проверяем что запрос всех питомцев возвращает  ошибку 500.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и получаем ошибку.
    Так как доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 500


def test_successful_add_photo_pet_with_no_valid_data(pet_photo='images/photo.docx'):
    """Проверяем возможность добовления фото  питомца, не поддерживаемый формат и должна быть ошибка"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    status, result = pf.set_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

    assert status == 500


def test_add_new_pet_with_no_valid_name(name='123456', animal_type='кот', age='2', pet_photo='images/cat.jpg'):
    """Проверяем что можно добавить питомца с не корректными данными поля name вводим цифры"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200

    assert result['name'] == name
    """питомец добавлен с именем из цифр"""


def test_add_new_pet_with_empty_name_ege_anymal(name='', animal_type='', age='', pet_photo='images/cat.jpg'):
    """Проверяем что можно добавить питомца с не корректными данными поля name, age, anymal_type пустые"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200

    assert result['name'] == ''
    """питомец добавлен с пустыми полями"""


def test_add_new_pet_without_photo_with_no_valid_age(name='плато', animal_type='дог', age=-4):
    """Проверяем что можно добавить питомца с отрицательным возрастом"""
    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)
    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] == ""
    """питомец добавлен с отрицательным возрастом"""


def test_successful_delete_self_pet_no_id():
    """Проверяем не  возможность удаления питомца при пустом id выдается ошибка"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # создаем id пустым
    pet_id = ''
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 404
