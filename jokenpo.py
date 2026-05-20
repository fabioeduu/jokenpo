from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_8F3tMOnsLlJg@ep-shiny-sunset-aq7qv8re-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    escolha_usuario = db.Column(db.String(20))
    escolha_computador = db.Column(db.String(20))
    resultado = db.Column(db.String(20))


with app.app_context():
    db.create_all()



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
        return jsonify({
            'error': 'Escolha inválida. Escolha entre pedra, papel ou tesoura.'
        }), 400

    computer_choice = random.choice(['pedra', 'papel', 'tesoura'])

    result = determine_winner(user_choice, computer_choice)

    if result == "Você":
        user_score += 1

    elif result == "Computador":
        computer_score += 1

    rounds += 1

    return jsonify({
        'result': result,
        'computer_choice': computer_choice,
        'score': {
            'user': user_score,
            'computer': computer_score,
            'rounds': rounds
        }
    })

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

    return jsonify({
        'message': 'Placar resetado!'
    })



@app.route('/players', methods=['POST'])
def create_player():

    data = request.get_json()

    novo_player = Player(
        nome=data['nome']
    )

    db.session.add(novo_player)
    db.session.commit()

    return jsonify({
        "message": "Jogador criado com sucesso"
    })



@app.route('/players', methods=['GET'])
def get_players():

    players = Player.query.all()

    resultado = []

    for p in players:
        resultado.append({
            "id": p.id,
            "nome": p.nome
        })

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)