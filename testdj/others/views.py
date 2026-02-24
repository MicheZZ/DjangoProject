from django.shortcuts import render
from django.http import JsonResponse
import random
import string


def index(request):
    return render(request, 'others/others.html')


def password_generator(request):
    password = None
    error = None

    if request.method == 'POST':
        try:
            length = int(request.POST.get('length', 12))
            use_uppercase = request.POST.get('uppercase') == 'on'
            use_numbers = request.POST.get('numbers') == 'on'
            use_symbols = request.POST.get('symbols') == 'on'

            if length < 4 or length > 128:
                error = 'Длина пароля должна быть от 4 до 128 символов'
            elif not (use_uppercase or use_numbers or use_symbols):
                error = 'Выберите хотя бы один тип символов'
            else:
                chars = string.ascii_lowercase
                if use_uppercase:
                    chars += string.ascii_uppercase
                if use_numbers:
                    chars += string.digits
                if use_symbols:
                    chars += '!@#$%^&*()_+-=[]{}|;:,.<>?'

                password = ''.join(random.choice(chars) for _ in range(length))
        except ValueError:
            error = 'Некорректное значение длины'

    context = {
        'password': password,
        'error': error,
    }
    return render(request, 'others/password_generator.html', context)


def fortune_teller(request):
    prediction = None
    bias = None
    error = None

    if request.method == 'POST':
        try:
            bias = int(request.POST.get('bias', 50))

            if bias < 0 or bias > 100:
                error = 'Значение должно быть от 0 до 100'
            else:
                # Генерируем случайное число от 0 до 100
                random_value = random.randint(0, 100)

                # Предсказания
                yes_predictions = [
                    '✨ Да, конечно! Это произойдёт!',
                    '🌟 Да, всё сложится отлично!',
                    '💫 Определённо - да!',
                    '🎯 Да, верьте в это!',
                    '🚀 Несомненно, да!',
                    '👍 Да, это случится!',
                ]

                no_predictions = [
                    '❌ Нет, не судьба',
                    '🌙 Нет, время ещё не пришло',
                    '⚡ Нет, выберите другой путь',
                    '🚫 Нет, это не сработает',
                    '😕 Нет, лучше подождать',
                    '👎 Нет, не стоит',
                ]

                maybe_predictions = [
                    '🤔 Может быть, зависит от вас',
                    '⚖️ Неясно, попробуйте ещё раз',
                    '🔮 Время покажет',
                    '📍 Возможно, если вы постараетесь',
                    '🌈 Шансы 50 на 50',
                    '💭 Очень неопределённо',
                ]

                # Сравниваем случайное число с предубеждением (bias)
                if random_value <= bias:
                    # Склоняется к "Да"
                    prediction_text = random.choice(yes_predictions)
                    prediction_type = 'yes'
                    prediction_type_display = '😊 Да!'
                    confidence = bias
                else:
                    # Склоняется к "Нет"
                    prediction_text = random.choice(no_predictions)
                    prediction_type = 'no'
                    prediction_type_display = '😞 Нет'
                    confidence = 100 - bias

                prediction = {
                    'text': prediction_text,
                    'type': prediction_type_display,
                    'type_class': prediction_type,
                    'confidence': confidence,
                }
        except ValueError:
            error = 'Ошибка при обработке данных'

    context = {
        'prediction': prediction,
        'bias': bias,
        'error': error,
    }
    return render(request, 'others/fortune_teller.html', context)


def number_converter(request):
    result = None
    error = None

    if request.method == 'POST':
        try:
            number = request.POST.get('number', '').strip().upper()
            from_base = int(request.POST.get('from_base', 10))
            to_base = int(request.POST.get('to_base', 10))

            if not number:
                error = 'Пожалуйста, введите число'
            elif from_base < 2 or from_base > 36:
                error = 'Исходная система счисления должна быть от 2 до 36'
            elif to_base < 2 or to_base > 36:
                error = 'Целевая система счисления должна быть от 2 до 36'
            else:
                try:
                    # Проверяем корректность числа для исходной системы
                    validate_number(number, from_base)

                    # Конвертируем из исходной системы в десятичную
                    decimal_value = int(number, from_base)

                    # Конвертируем из десятичной в целевую систему
                    if to_base == 10:
                        converted = str(decimal_value)
                    else:
                        converted = dec_to_base(decimal_value, to_base)

                    result = {
                        'original': number,
                        'from_base': from_base,
                        'to_base': to_base,
                        'decimal': decimal_value,
                        'converted': converted,
                    }
                except ValueError as e:
                    error = str(e)
        except Exception as e:
            error = f'Ошибка: {str(e)}'

    context = {
        'result': result,
        'error': error,
    }
    return render(request, 'others/number_converter.html', context)


def validate_number(number, base):
    """Проверяет корректность числа для заданной системы счисления"""
    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    valid_digits = digits[:base]

    for char in number:
        if char not in valid_digits:
            raise ValueError(
                f'Символ "{char}" недопустим для системы счисления с основанием {base}. '
                f'Допустимые символы: {valid_digits}'
            )


def dec_to_base(num, base):
    """Конвертирует десятичное число в систему с заданным основанием"""
    if num == 0:
        return '0'

    digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''

    while num > 0:
        result = digits[num % base] + result
        num //= base

    return result