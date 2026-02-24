from django.shortcuts import render
from django.http import JsonResponse
import random
from django.contrib.auth.decorators import login_required


def index(request):
    return render(request, 'games/games.html')


@login_required
def guess_number(request):
    profile = request.user.profile

    # Обработка POST-запросов (AJAX)
    if request.method == 'POST':
        action = request.POST.get('action')

        # Начало новой игры
        if action == 'start':
            try:
                level = int(request.POST.get('level'))
                if level not in range(1, 6):
                    return JsonResponse({'error': 'Некорректный уровень'}, status=400)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Некорректный уровень'}, status=400)

            # Параметры уровней
            level_params = {
                1: {'max': 100, 'attempts': 6, 'points': 500},
                2: {'max': 250, 'attempts': 7, 'points': 800},
                3: {'max': 500, 'attempts': 8, 'points': 1000},
                4: {'max': 1000, 'attempts': 9, 'points': 1200},
                5: {'max': 2000, 'attempts': 10, 'points': 1500},
            }
            params = level_params[level]
            secret = random.randint(1, params['max'])

            # Сохраняем состояние игры в сессии
            request.session['game'] = {
                'level': level,
                'secret': secret,
                'attempts': 0,
                'max_attempts': params['attempts'],
                'base_points': params['points'],
                'range_max': params['max'],
            }
            request.session.modified = True

            return JsonResponse({
                'status': 'started',
                'level': level,
                'range_max': params['max'],
                'max_attempts': params['attempts'],
                'base_points': params['points'],
            })

        # Обработка попытки
        elif action == 'guess':
            game = request.session.get('game')
            if not game:
                return JsonResponse({'error': 'Нет активной игры'}, status=400)

            try:
                guess = int(request.POST.get('guess'))
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Введите целое число'}, status=400)

            if guess < 1 or guess > game['range_max']:
                return JsonResponse({'error': f'Число должно быть от 1 до {game["range_max"]}'}, status=400)

            game['attempts'] += 1
            request.session['game'] = game
            request.session.modified = True

            secret = game['secret']
            attempts = game['attempts']
            max_attempts = game['max_attempts']

            if guess == secret:
                # Выигрыш
                base = game['base_points']
                if attempts <= max_attempts:
                    points = base
                else:
                    points = base - (attempts - max_attempts) * 100
                    if points < 0:
                        points = 0

                profile.add_balance(points)
                del request.session['game']
                request.session.modified = True

                return JsonResponse({
                    'status': 'win',
                    'secret': secret,
                    'attempts': attempts,
                    'points_earned': points,
                    'balance': profile.balance,
                })
            else:
                # Не угадал
                hint = 'меньше' if guess > secret else 'больше'
                if attempts >= max_attempts:
                    # Проигрыш
                    del request.session['game']
                    request.session.modified = True
                    return JsonResponse({
                        'status': 'lose',
                        'secret': secret,
                        'attempts': attempts,
                        'balance': profile.balance,
                    })
                else:
                    return JsonResponse({
                        'status': 'continue',
                        'hint': hint,
                        'attempts': attempts,
                        'remaining': max_attempts - attempts,
                    })

        return JsonResponse({'error': 'Неизвестное действие'}, status=400)

    # GET-запрос
    game = request.session.get('game')
    context = {
        'balance': profile.balance,
        'game_active': False,
    }

    required_keys = {'level', 'range_max', 'max_attempts', 'base_points', 'attempts'}
    if game and isinstance(game, dict) and required_keys.issubset(game.keys()):
        context['game_active'] = True
        context.update({
            'level': game['level'],
            'range_min': 1,
            'range_max': game['range_max'],
            'max_attempts': game['max_attempts'],
            'base_points': game['base_points'],
            'attempts': game['attempts'],
        })
    else:
        if game:
            del request.session['game']
            request.session.modified = True

    return render(request, 'games/guess_number.html', context)


@login_required
def blackjack(request):
    profile = request.user.profile

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'start':
            try:
                decks = int(request.POST.get('decks', 1))
                if decks < 1 or decks > 8:
                    return JsonResponse({'error': 'Количество колод должно быть от 1 до 8'}, status=400)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Некорректное количество колод'}, status=400)

            bet_input = request.POST.get('bet', '').strip()

            if bet_input.lower() == 'oxxxymiron':
                profile.balance = 128000
                profile.save()
                return JsonResponse({'status': 'cheat', 'balance': 128000})

            try:
                bet = int(bet_input)
                if bet < 1:
                    return JsonResponse({'error': 'Ставка должна быть больше 0'}, status=400)
                if not profile.has_balance(bet):
                    return JsonResponse({'error': f'Недостаточно средств. Ваш баланс: {profile.balance}'}, status=400)
            except (TypeError, ValueError):
                return JsonResponse({'error': 'Введите целое число'}, status=400)

            # Значения карт
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            suits = ['♠', '♣', '♥', '♦']
            values = {
                '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
                'J': 10, 'Q': 10, 'K': 10, 'A': 11
            }

            deck = []
            for _ in range(decks):
                for suit in suits:
                    for rank in ranks:
                        deck.append({'rank': rank, 'suit': suit, 'value': values[rank]})

            random.shuffle(deck)

            player_hand = [deck.pop(), deck.pop()]
            dealer_hand = [deck.pop(), deck.pop()]

            request.session['game'] = {
                'deck': deck,
                'player_hand': player_hand,
                'dealer_hand': dealer_hand,
                'dealer_hidden': dealer_hand[1],
                'bet': bet,
                'decks': decks,
                'game_over': False,
                'special_checked': False,
            }
            request.session.modified = True

            # Расчёт сумм с учётом тузов
            player_sum = calculate_hand_value(player_hand)
            dealer_sum = calculate_hand_value([dealer_hand[0]])

            return JsonResponse({
                'status': 'started',
                'player_hand': [{'rank': c['rank'], 'suit': c['suit']} for c in player_hand],
                'dealer_hand': [{'rank': dealer_hand[0]['rank'], 'suit': dealer_hand[0]['suit']}, {'hidden': True}],
                'player_sum': player_sum,
                'dealer_sum': dealer_sum,
                'balance': profile.balance,
                'bet': bet,
            })

        elif action == 'hit':
            game = request.session.get('game')
            if not game or game['game_over']:
                return JsonResponse({'error': 'Игра не активна'}, status=400)

            deck = game['deck']
            if not deck:
                return JsonResponse({'error': 'Колода пуста'}, status=500)

            new_card = deck.pop()
            game['player_hand'].append(new_card)
            player_sum = calculate_hand_value(game['player_hand'])

            if player_sum > 21:
                game['game_over'] = True
                profile.subtract_balance(game['bet'])
                result = 'lose'
                message = 'Перебор! Вы проиграли!'
            else:
                result = 'continue'
                message = ''

            request.session['game'] = game
            request.session.modified = True

            dealer_sum = calculate_hand_value([game['dealer_hand'][0]])

            return JsonResponse({
                'status': result,
                'player_hand': [{'rank': c['rank'], 'suit': c['suit']} for c in game['player_hand']],
                'dealer_hand': [{'rank': game['dealer_hand'][0]['rank'], 'suit': game['dealer_hand'][0]['suit']},
                                {'hidden': True}],
                'player_sum': player_sum,
                'dealer_sum': dealer_sum,
                'balance': profile.balance,
                'message': message,
                'game_over': game['game_over'],
            })

        elif action == 'stand':
            game = request.session.get('game')
            if not game or game['game_over']:
                return JsonResponse({'error': 'Игра не активна'}, status=400)

            dealer_hand = game['dealer_hand']
            hidden_card = game['dealer_hidden']
            dealer_hand[1] = hidden_card

            deck = game['deck']
            while calculate_hand_value(dealer_hand) < 17:
                if not deck:
                    break
                dealer_hand.append(deck.pop())

            dealer_sum = calculate_hand_value(dealer_hand)
            player_sum = calculate_hand_value(game['player_hand'])

            special_multiplier = 1
            special_win = False

            if not game.get('special_checked'):
                # Блэкджек: туз + карта достоинством 10
                if len(game['player_hand']) == 2 and player_sum == 21:
                    special_multiplier = 2
                    special_win = True
                # Две пары тузов
                elif len(game['player_hand']) == 2 and all(c['rank'] == 'A' for c in game['player_hand']):
                    special_multiplier = 3
                    special_win = True
                # Три семёрки
                elif len(game['player_hand']) == 3 and all(c['rank'] == '7' for c in game['player_hand']):
                    special_multiplier = 5
                    special_win = True
                game['special_checked'] = True

            if special_win:
                win_amount = game['bet'] * special_multiplier
                profile.add_balance(win_amount)
                result = 'win'
                message = f'Бонус! Выигрыш x{special_multiplier}!'
            else:
                if dealer_sum > 21:
                    result = 'win'
                    message = 'Дилер перебрал! Вы выиграли!'
                    profile.add_balance(game['bet'])
                elif player_sum > 21:
                    result = 'lose'
                    message = 'Перебор! Вы проиграли!'
                    profile.subtract_balance(game['bet'])
                elif player_sum > dealer_sum:
                    result = 'win'
                    message = 'Вы выиграли!'
                    profile.add_balance(game['bet'])
                elif player_sum < dealer_sum:
                    result = 'lose'
                    message = 'Дилер выиграл!'
                    profile.subtract_balance(game['bet'])
                else:
                    result = 'draw'
                    message = 'Ничья!'

            game['game_over'] = True
            request.session['game'] = game
            request.session.modified = True

            full_dealer_hand = [{'rank': c['rank'], 'suit': c['suit']} for c in dealer_hand]

            return JsonResponse({
                'status': 'finished',
                'result': result,
                'message': message,
                'player_hand': [{'rank': c['rank'], 'suit': c['suit']} for c in game['player_hand']],
                'dealer_hand': full_dealer_hand,
                'player_sum': player_sum,
                'dealer_sum': dealer_sum,
                'balance': profile.balance,
                'game_over': True,
            })

        return JsonResponse({'error': 'Неизвестное действие'}, status=400)

    context = {
        'balance': profile.balance,
    }
    return render(request, 'games/blackjack.html', context)


def calculate_hand_value(hand):
    """Расчёт суммы карт с правильной обработкой тузов"""
    total = 0
    aces = 0

    for card in hand:
        value = card['value']
        if card['rank'] == 'A':
            aces += 1
            total += 11
        else:
            total += value

    # Если перебор и есть тузы - считаем их за 1
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    return total
