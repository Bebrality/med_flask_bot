from flask import Flask, render_template, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data.json"


def load(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []


def save(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)



@app.route("/meds")
def meds():
    return jsonify(load(DATA_FILE))


@app.route("/take/<int:id>")
def take(id):
    data = load(DATA_FILE)

    for m in data:
        if m["id"] == id:
            m["taken"] = True

    save(DATA_FILE, data)
    return jsonify({"status": "ok"})



@app.route("/delete/<int:id>")
def delete(id):
    data = load(DATA_FILE)
    data = [m for m in data if m["id"] != id]
    save(DATA_FILE, data)
    return jsonify({"status": "deleted"})



@app.route("/clear")
def clear():
    save(DATA_FILE, [])
    return jsonify({"status": "cleared"})


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name")
    time = request.form.get("time")

    data = load(DATA_FILE)

    med = {
        "id": max([m["id"] for m in data], default=0) + 1,
        "name": name,
        "time": time,
        "taken": False
    }

    data.append(med)
    save(DATA_FILE, data)

    return jsonify({"status": "ok"})



def bot_response(text):
    text = text.lower()

    if text.startswith("добавить"):
        try:
            _, name, time = text.split()
            data = load(DATA_FILE)

            med = {
                "id": max([m["id"] for m in data], default=0) + 1,
                "name": name,
                "time": time,
                "taken": False
            }

            data.append(med)
            save(DATA_FILE, data)

            return f"Добавил {name} на {time}"
        except:
            return "Пример: добавить нурофен 12:00"

    elif "привет" in text:
        return "Привет 😄"

    elif "кто тебя создал" in text:
        return "Тимур 😎"

    elif "2+2" in text:
        return "4"

    elif "что ты умеешь" in text:
        return "Я храню данные о ваших лекарствах и напоминаю вам когда их нужно принимать"

    elif "помощь" in text:
        return "Вы можете добавить лекарства в правом окне либо написав мне напрямую через команду добавить, в нужное время вам придет уведомление, после принятия лекарства не забудьте это отметить"


    return "Не понял"


@app.route("/", methods=["GET", "POST"])
def index():
    response = ""

    if request.method == "POST":
        user_input = request.form.get("message")
        if user_input:
            response = bot_response(user_input)

    return render_template("index.html", response=response)

@app.route("/check_time")
def check_time():
    from datetime import datetime
    now = datetime.now().strftime("%H:%M")

    data = load(DATA_FILE)

    due = []
    for m in data:
        if m["time"] == now and not m["taken"]:
            due.append(m)

    return jsonify(due)


if __name__ == "__main__":
    app.run(debug=True)