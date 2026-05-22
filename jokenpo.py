import os
import urllib.parse
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)

DB_USER     = os.environ.get("DB_USER",     "seu_usuario")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "sua_senha")
DB_HOST     = os.environ.get("DB_HOST",     "seu-server.database.windows.net")
DB_NAME     = os.environ.get("DB_NAME",     "db-dimdim")

safe_password = urllib.parse.quote_plus(DB_PASSWORD)

conn_str = f"mssql+pymssql://{DB_USER}:{safe_password}@{DB_HOST}/{DB_NAME}"

app.config["SQLALCHEMY_DATABASE_URI"]        = conn_str
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Jogador(db.Model):
    __tablename__ = "jogadores"

    id        = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome      = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.now)

    partidas  = db.relationship("Partida", backref="jogador", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":        self.id,
            "nome":      self.nome,
            "criado_em": self.criado_em.isoformat() if self.criado_em else None
        }


class Partida(db.Model):
    __tablename__ = "partidas"

    id                 = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jogador_id         = db.Column(db.Integer, db.ForeignKey("jogadores.id"), nullable=False)
    escolha_jogador    = db.Column(db.String(10), nullable=False)
    escolha_computador = db.Column(db.String(10), nullable=False)
    resultado          = db.Column(db.String(15), nullable=False)
    jogada_em          = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id":                 self.id,
            "jogador_id":         self.jogador_id,
            "escolha_jogador":    self.escolha_jogador,
            "escolha_computador": self.escolha_computador,
            "resultado":          self.resultado,
            "jogada_em":          self.jogada_em.isoformat() if self.jogada_em else None
        }


with app.app_context():
    db.create_all()


OPCOES = ["pedra", "papel", "tesoura"]

def determinar_vencedor(jogador, computador):
    if jogador == computador:
        return "Empate"
    ganhos = {("pedra", "tesoura"), ("tesoura", "papel"), ("papel", "pedra")}
    return "Você" if (jogador, computador) in ganhos else "Computador"  


@app.route("/")
def index():
    return jsonify({"message": "Bem-vindo ao Jokenpô API! Endpoints principais: /jogadores e /play"})


@app.route("/jogadores", methods=["POST"])
def criar_jogador():
    dados = request.get_json()
    if not dados or not dados.get("nome"):
        return jsonify({"error": "Campo 'nome' é obrigatório."}), 400

    jogador = Jogador(nome=dados["nome"].strip())
    db.session.add(jogador)
    db.session.commit()
    return jsonify(jogador.to_dict()), 201


@app.route("/jogadores", methods=["GET"])
def listar_jogadores():
    jogadores = Jogador.query.order_by(Jogador.criado_em.desc()).all()
    return jsonify([j.to_dict() for j in jogadores])


@app.route("/jogadores/<int:jogador_id>", methods=["GET"])
def obter_jogador(jogador_id):
    jogador = Jogador.query.get_or_404(jogador_id)
    return jsonify(jogador.to_dict())


@app.route("/jogadores/<int:jogador_id>", methods=["PUT"])
def atualizar_jogador(jogador_id):
    jogador = Jogador.query.get_or_404(jogador_id)
    dados = request.get_json()
    if not dados or not dados.get("nome"):
        return jsonify({"error": "Campo 'nome' é obrigatório."}), 400

    jogador.nome = dados["nome"].strip()
    db.session.commit()
    return jsonify(jogador.to_dict())


@app.route("/jogadores/<int:jogador_id>", methods=["DELETE"])
def deletar_jogador(jogador_id):
    jogador = Jogador.query.get_or_404(jogador_id)
    db.session.delete(jogador)
    db.session.commit()
    return jsonify({"message": f"Jogador '{jogador.nome}' e suas partidas foram deletados com sucesso."})


@app.route("/play", methods=["POST"])
def jogar():
    dados = request.get_json()
    if not dados:
        return jsonify({"error": "Body JSON obrigatório."}), 400

    jogador_id = dados.get("jogador_id")
    escolha    = dados.get("choice", "").lower()  

    if not jogador_id:
        return jsonify({"error": "Campo 'jogador_id' é obrigatório."}), 400
    if escolha not in OPCOES:
        return jsonify({"error": "Escolha inválida. Use: pedra, papel ou tesoura."}), 400

    jogador = Jogador.query.get_or_404(jogador_id)

    computador = random.choice(OPCOES)
    resultado  = determinar_vencedor(escolha, computador)

    partida = Partida(
        jogador_id         = jogador.id,
        escolha_jogador    = escolha,
        escolha_computador = computador,
        resultado          = resultado
    )
    db.session.add(partida)
    db.session.commit()

    vitorias = Partida.query.filter_by(jogador_id=jogador.id, resultado="Você").count()
    derrotas = Partida.query.filter_by(jogador_id=jogador.id, resultado="Computador").count()
    empates  = Partida.query.filter_by(jogador_id=jogador.id, resultado="Empate").count()
    total    = vitorias + derrotas + empates

    return jsonify({
        "partida": partida.to_dict(),
        "placar": {
            "jogador":  jogador.nome,
            "vitorias": vitorias,
            "derrotas": derrotas,
            "empates":  empates,
            "total":    total
        }
    }), 201


@app.route("/partidas", methods=["GET"])
def listar_partidas():
    jogador_id = request.args.get("jogador_id", type=int)
    query = Partida.query.order_by(Partida.jogada_em.desc())
    if jogador_id:
        query = query.filter_by(jogador_id=jogador_id)
    return jsonify([p.to_dict() for p in query.all()])


@app.route("/partidas/<int:partida_id>", methods=["GET"])
def obter_partida(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    return jsonify(partida.to_dict())


@app.route("/partidas/<int:partida_id>", methods=["DELETE"])
def deletar_partida(partida_id):
    partida = Partida.query.get_or_404(partida_id)
    db.session.delete(partida)
    db.session.commit()
    return jsonify({"message": f"Partida #{partida_id} deletada com sucesso."})


@app.route("/jogadores/<int:jogador_id>/reset", methods=["POST"])
def reset_jogador(jogador_id):
    jogador = Jogador.query.get_or_404(jogador_id)
    Partida.query.filter_by(jogador_id=jogador.id).delete()
    db.session.commit()
    return jsonify({"message": f"Placar de '{jogador.nome}' resetado com sucesso."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
