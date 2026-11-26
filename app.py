import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave_secreta_noticias_cn2")

# Conexión al contenedor PostgreSQL (usa el nombre del servicio 'db_noticias')
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin1234@db_noticias:5432/noticias_db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# Modelo de la tabla que se creará automáticamente en PostgreSQL / Adminer
class Noticia(db.Model):
    __tablename__ = "noticias"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    autor = db.Column(db.String(100), nullable=False, default="Anónimo")
    fecha_publicacion = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Noticia {self.id} - {self.titulo}>"


# Crear las tablas automáticamente al iniciar el contenedor
with app.app_context():
    db.create_all()


# READ: Listar todas las noticias
@app.route("/")
def index():
    noticias = Noticia.query.order_by(Noticia.id.desc()).all()
    return render_template("index.html", noticias=noticias)


# CREATE: Agregar una nueva noticia
@app.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        contenido = request.form.get("contenido", "").strip()
        autor = request.form.get("autor", "Anónimo").strip() or "Anónimo"

        if not titulo or not contenido:
            flash("El título y el contenido son obligatorios.", "error")
            return redirect(url_for("crear"))

        nueva_noticia = Noticia(
            titulo=titulo,
            contenido=contenido,
            autor=autor
        )
        db.session.add(nueva_noticia)
        db.session.commit()
        flash("Noticia creada correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("crear.html")


# UPDATE: Editar una noticia existente
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    noticia = db.get_or_404(Noticia, id)

    if request.method == "POST":
        noticia.titulo = request.form.get("titulo", noticia.titulo).strip()
        noticia.contenido = request.form.get("contenido", noticia.contenido).strip()
        noticia.autor = request.form.get("autor", noticia.autor).strip() or "Anónimo"

        db.session.commit()
        flash("Noticia actualizada correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("editar.html", noticia=noticia)


# DELETE: Eliminar una noticia
@app.route("/eliminar/<int:id>", methods=["POST", "GET"])
def eliminar(id):
    noticia = db.get_or_404(Noticia, id)
    db.session.delete(noticia)
    db.session.commit()
    flash("Noticia eliminada correctamente.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)