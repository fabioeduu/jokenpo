from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# CONFIGURAÇÃO DO BANCO NEON
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jokenpo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    player_id = db.Column(
        db.Integer,
        db.ForeignKey('player.id')
    )

    escolha_usuario = db.Column(db.String(20))
    escolha_computador = db.Column(db.String(20))
    resultado = db.Column(db.String(20))

# =========================
# CRIAR TABELAS
# =========================

with app.app_context():
    db.create_all()

# =========================
# VARIÁVEIS GLOBAIS
# =========================

user_score = 0
computer_score = 0
rounds = 0

# =========================
# ROTAS
# =========================

@app.route('/')
def index():
    return "Bem-vindo ao Jokenpô API"

@app.route('/teste')
def teste():
    return "API funcionando"

# =========================
# JOGAR
# =========================

@app.route('/play', methods=['POST'])
def play_game():

    global user_score
    global computer_score
    global rounds

    data = request.get_json()

    user_choice = data.get('choice', '').lower()
    player_id = data.get('player_id')

    if user_choice not in ['pedra', 'papel', 'tesoura']:

        return jsonify({
            'error': 'Escolha inválida'
        }), 400

    computer_choice = random.choice([
        'pedra',
        'papel',
        'tesoura'
    ])

    result = determine_winner(
        user_choice,
        computer_choice
    )

    if result == "Você":
        user_score += 1

    elif result == "Computador":
        computer_score += 1

    rounds += 1

    # SALVAR PARTIDA
    partida = Match(
        player_id=player_id,
        escolha_usuario=user_choice,
        escolha_computador=computer_choice,
        resultado=result
    )

    db.session.add(partida)
    db.session.commit()

    return jsonify({

        'result': result,

        'computer_choice': computer_choice,

        'score': {
            'user': user_score,
            'computer': computer_score,
            'rounds': rounds
        }

    })

# =========================
# DEFINIR VENCEDOR
# =========================

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

# =========================
# RESET SCORE
# =========================

@app.route('/reset', methods=['POST'])
def reset_score():

    global user_score
    global computer_score
    global rounds

    user_score = 0
    computer_score = 0
    rounds = 0

    return jsonify({
        'message': 'Placar resetado'
    })

# =========================
# CRIAR PLAYER
# =========================

@app.route('/players', methods=['POST'])
def create_player():

    data = request.get_json()

    novo_player = Player(
        nome=data['nome']
    )

    db.session.add(novo_player)
    db.session.commit()

    return jsonify({
        'message': 'Jogador criado',
        'id': novo_player.id
    })

# =========================
# LISTAR PLAYERS
# =========================

@app.route('/players', methods=['GET'])
def get_players():

    players = Player.query.all()

    resultado = []

    for p in players:

        resultado.append({
            'id': p.id,
            'nome': p.nome
        })

    return jsonify(resultado)

# =========================
# LISTAR PARTIDAS
# =========================

@app.route('/matches', methods=['GET'])
def get_matches():

    matches = Match.query.all()

    resultado = []

    for m in matches:

        resultado.append({

            'id': m.id,
            'player_id': m.player_id,
            'escolha_usuario': m.escolha_usuario,
            'escolha_computador': m.escolha_computador,
            'resultado': m.resultado

        })

    return jsonify(resultado)

# =========================
# START APP
# =========================

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000
    )