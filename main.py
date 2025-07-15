from flask import Flask, request, render_template, redirect
import os, json

app = Flask(__name__)
os.makedirs("scripts", exist_ok=True)
DB = "scripts/list.json"
SUGGESTIONS_DB = "scripts/suggestions.json"  # Asegúrate de que esta base de datos existe.

if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump([], f)

if not os.path.exists(SUGGESTIONS_DB):
    with open(SUGGESTIONS_DB, "w") as f:
        json.dump([], f)

def load_scripts():
    with open(DB, "r") as f:
        return json.load(f)

def save_script(nombre, codigo):
    filename = nombre.lower().replace(" ", "-") + ".lsp"
    filepath = os.path.join("scripts", filename)
    with open(filepath, "w") as f:
        f.write(codigo)
    data = load_scripts()
    data.append({"nombre": nombre, "archivo": filename})
    with open(DB, "w") as f:
        json.dump(data, f)

def load_suggestions():
    with open(SUGGESTIONS_DB, "r") as f:
        return json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        codigo = request.form.get("codigo")
        if nombre and codigo:
            save_script(nombre, codigo)
            return redirect("/")

    scripts = load_scripts()
    bloques = []
    for s in scripts:
        try:
            with open(os.path.join("scripts", s["archivo"])) as f:
                contenido = f.read()
        except:
            contenido = "(error al leer archivo)"
        bloques.append({"nombre": s["nombre"], "codigo": contenido})

    suggestions = load_suggestions()  # Carga las sugerencias
    return render_template("index.html", bloques=bloques, suggestions=suggestions)

@app.route("/scripts/<archivo>")
def ver_script(archivo):
    return open(os.path.join("scripts", archivo)).read(), 200, {'Content-Type': 'text/plain'}

@app.route("/editar_sugerencia/<int:suggestion_id>", methods=["POST"])
def editar_sugerencia(suggestion_id):
    titulo = request.form.get("titulo")
    contenido = request.form.get("contenido")

    if titulo and contenido:
        suggestions = load_suggestions()
        if 0 <= suggestion_id < len(suggestions):
            suggestions[suggestion_id]["titulo"] = titulo
            suggestions[suggestion_id]["contenido"] = contenido
            with open(SUGGESTIONS_DB, "w") as f:
                json.dump(suggestions, f)

    return redirect("/#sugerencias")

@app.route("/eliminar_sugerencia/<int:suggestion_id>", methods=["POST"])
def eliminar_sugerencia(suggestion_id):
    suggestions = load_suggestions()
    if 0 <= suggestion_id < len(suggestions):
        suggestions.pop(suggestion_id)  # Elimina la sugerencia
        with open(SUGGESTIONS_DB, "w") as f:
            json.dump(suggestions, f)

    return redirect("/#sugerencias")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # Cambié el puerto a 5000 para desarrollo
