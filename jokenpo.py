from flask import Flask, request, jsonify
import random

app = Flask(__name__)

user_score = 0
computer_score = 0
rounds = 0

@app.route('/teste')
def teste():
    return "Funcionando, para CheckPoint3"

@app.route('/')
def index():
    return "Bem-vindo ao Jogo de Jokenpô! Use a rota /play para jogar."

@app.route('/play', methods=['POST'])
def play_game():
    global user_score, computer_score, rounds

    user_choice = request.json.get('choice', '').lower()

    if user_choice not in ['pedra', 'papel', 'tesoura']:
        return jsonify({'error': 'Escolha inválida. Escolha entre pedra, papel ou tesoura.'}), 400
    
    computer_choice = random.choice(['pedra', 'papel', 'tesoura'])
    result = determine_winner(user_choice, computer_choice)

    if result == "Empate":
        return jsonify({'result': 'Empate', 'computer_choice': computer_choice, 'score': {'user': user_score, 'computer': computer_score, 'rounds': rounds}})
    elif result == "Você":
        user_score += 1
    else:
        computer_score += 1

    rounds += 1
    return jsonify({'result': result, 'computer_choice': computer_choice, 'score': {'user': user_score, 'computer': computer_score, 'rounds': rounds}})

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Empate"
    elif (
        (user_choice == "pedra" and computer_choice == "tesoura") or
        (user_choice == "tesoura" and computer_choice == "papel") or
        (user_choice == "papel" and computer_choice == "pedra")
    ):
        return "Você"
    else:
        return "Computador"

@app.route('/reset', methods=['POST'])
def reset_score():
    global user_score, computer_score, rounds
    user_score = 0
    computer_score = 0
    rounds = 0
    return jsonify({'message': 'Placar resetado!'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
