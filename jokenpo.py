import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)

# Configuração do PostgreSQL (Neon) vinda do primeiro código
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://neondb_owner:npg_8F3tMOnsLlJg@ep-shiny-sunset-aq7qv8re.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
 
# MODELOS DE DADOS
class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Deleção em cascata: se o player for deletado, suas matches também serão
    matches = db.relationship("Match", backref="player", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None
        }

class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    escolha_usuario = db.Column(db.String(20), nullable=False)
    escolha_computador = db.Column(db.String(20), nullable=False)
    resultado = db.Column(db.String(20), nullable=False)
    jogada_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "escolha_usuario": self.escolha_usuario,
            "escolha_computador": self.escolha_computador,
            "resultado": self.resultado,
            "jogada_em": self.jogada_em.isoformat() if self.jogada_em else None
        }

with app.app_context():
    db.create_all()


# LOGICA DO JOGO - JOKENPO
OPCOES = ["pedra", "papel", "tesoura"]

def determinar_vencedor(jogador, computador):
    if jogador == computador:
        return "Empate"
    
    ganhos = {("pedra", "tesoura"), ("tesoura", "papel"), ("papel", "pedra")}
    return "Você" if (jogador, computador) in ganhos else "Computador"

@app.route("/")
def index():
    return jsonify({"message": "Bem-vindo ao Jokenpô API! Endpoints principais: /players e /play"})


@app.route("/play", methods=["POST"])
def jogar():
    dados = request.get_json(silent=True) or {}
    jogador_id = dados.get("player_id")
    escolha_usuario = dados.get("choice", "").lower()

    if not jogador_id:
        return jsonify({"error": "Campo 'player_id' é obrigatório."}), 400
    if escolha_usuario not in OPCOES:
        return jsonify({"error": "Escolha inválida. Use: pedra, papel ou tesoura."}), 400

    # Verifica se o jogador existe
    player = Player.query.get_or_404(jogador_id)

    escolha_computador = random.choice(OPCOES)
    resultado = determinar_vencedor(escolha_usuario, escolha_computador)

    # Salva a partida
    match = Match(
        player_id=player.id,
        escolha_usuario=escolha_usuario,
        escolha_computador=escolha_computador,
        resultado=resultado
    )
    db.session.add(match)
    db.session.commit()

    # Calcula o placar dinamicamente usando o banco de dados
    vitorias = Match.query.filter_by(player_id=player.id, resultado="Você").count()
    derrotas = Match.query.filter_by(player_id=player.id, resultado="Computador").count()
    empates = Match.query.filter_by(player_id=player.id, resultado="Empate").count()
    total = vitorias + derrotas + empates

    return jsonify({
        "partida": match.to_dict(),
        "placar": {
            "jogador": player.nome,
            "vitorias": vitorias,
            "derrotas": derrotas,
            "empates": empates,
            "total_partidas": total
        }
    }), 201


@app.route("/players/<int:player_id>/reset", methods=["POST"])
def reset_jogador(player_id):
    # Apaga apenas o histórico de partidas do jogador específico
    player = Player.query.get_or_404(player_id)
    Match.query.filter_by(player_id=player.id).delete()
    db.session.commit()
    return jsonify({"message": f"Placar de '{player.nome}' resetado com sucesso."})

# CRUD - JOGADORES (PLAYERS)
@app.route("/players", methods=["POST"])
def create_player():
    dados = request.get_json(silent=True) or {}
    if not dados.get("nome"):
        return jsonify({"error": "Campo 'nome' é obrigatório."}), 400

    player = Player(nome=dados["nome"].strip())
    db.session.add(player)
    db.session.commit()
    
    return jsonify(player.to_dict()), 201


@app.route("/players", methods=["GET"])
def listar_jogadores():
    players = Player.query.order_by(Player.criado_em.desc()).all()
    return jsonify([p.to_dict() for p in players])


@app.route("/players/<int:player_id>", methods=["GET"])
def obter_jogador(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(player.to_dict())


@app.route("/players/<int:player_id>", methods=["PUT"])
def atualizar_jogador(player_id):
    player = Player.query.get_or_404(player_id)
    dados = request.get_json(silent=True) or {}
    
    if not dados.get("nome"):
        return jsonify({"error": "Campo 'nome' é obrigatório para atualizar."}), 400

    player.nome = dados["nome"].strip()
    db.session.commit()
    return jsonify(player.to_dict())


@app.route("/players/<int:player_id>", methods=["DELETE"])
def deletar_jogador(player_id):
    player = Player.query.get_or_404(player_id)
    # Graças ao cascade="all, delete-orphan", não precisamos deletar as partidas manualmente aqui
    db.session.delete(player)
    db.session.commit()
    return jsonify({"message": f"Jogador '{player.nome}' e suas partidas foram deletados."})

# CRUD - PARTIDAS (MATCHES)
@app.route("/matches", methods=["GET"])
def listar_partidas():
    player_id = request.args.get("player_id", type=int)
    query = Match.query.order_by(Match.jogada_em.desc())
    
    # Permite filtrar as partidas passando ?player_id=1 na URL
    if player_id:
        query = query.filter_by(player_id=player_id)
        
    return jsonify([m.to_dict() for m in query.all()])


@app.route("/matches/<int:match_id>", methods=["GET"])
def obter_partida(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify(match.to_dict())


@app.route("/matches/<int:match_id>", methods=["DELETE"])
def deletar_partida(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify({"message": f"Partida #{match_id} deletado com sucesso!!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)