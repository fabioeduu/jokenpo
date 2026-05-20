import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://neondb_owner:npg_8F3tMOnsLlJg@ep-shiny-sunset-aq7qv8re.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"))
    escolha_usuario = db.Column(db.String(20))
    escolha_computador = db.Column(db.String(20))
    resultado = db.Column(db.String(20))

with app.app_context():
    db.create_all()

user_score = 0
computer_score = 0
rounds = 0


@app.route("/")
def index():
    return "API Jokenpô OK"


@app.route("/teste")
def teste():
    return "OK"


@app.route("/play", methods=["POST"])
def play_game():
    global user_score, computer_score, rounds

    data = request.get_json(silent=True) or {}

    user_choice = (data.get("choice") or "").lower()
    player_id = data.get("player_id")

    if user_choice not in ["pedra", "papel", "tesoura"]:
        return jsonify({"error": "Escolha inválida"}), 400

    computer_choice = random.choice(["pedra", "papel", "tesoura"])

    result = determine_winner(user_choice, computer_choice)

    if result == "Você":
        user_score += 1
    elif result == "Computador":
        computer_score += 1

    rounds += 1

    if player_id:
        match = Match(
            player_id=player_id,
            escolha_usuario=user_choice,
            escolha_computador=computer_choice,
            resultado=result
        )
        db.session.add(match)
        db.session.commit()

    return jsonify({
        "result": result,
        "computer_choice": computer_choice,
        "score": {
            "user": user_score,
            "computer": computer_score,
            "rounds": rounds
        }
    })


def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "Empate"

    if (
        (user_choice == "pedra" and computer_choice == "tesoura")
        or (user_choice == "tesoura" and computer_choice == "papel")
        or (user_choice == "papel" and computer_choice == "pedra")
    ):
        return "Você"

    return "Computador"


@app.route("/reset", methods=["POST"])
def reset_score():
    global user_score, computer_score, rounds

    user_score = 0
    computer_score = 0
    rounds = 0

    return jsonify({"message": "Placar resetado"})


@app.route("/players", methods=["POST"])
def create_player():
    data = request.get_json(silent=True) or {}

    if "nome" not in data:
        return jsonify({"error": "Nome obrigatório"}), 400

    player = Player(nome=data["nome"])

    db.session.add(player)
    db.session.commit()

    return jsonify({
        "message": "Jogador criado",
        "id": player.id
    })


@app.route("/players", methods=["GET"])
def get_players():
    players = Player.query.all()

    return jsonify([
        {"id": p.id, "nome": p.nome}
        for p in players
    ])


@app.route("/matches", methods=["GET"])
def get_matches():
    matches = Match.query.all()

    return jsonify([
        {
            "id": m.id,
            "player_id": m.player_id,
            "escolha_usuario": m.escolha_usuario,
            "escolha_computador": m.escolha_computador,
            "resultado": m.resultado
        }
        for m in matches
    ])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)