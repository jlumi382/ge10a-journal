from flask import Flask, render_template

app = Flask(__name__)

# Home Route
@app.route("/")
def home():
    return render_template("index.html")

# Category Route
@app.route("/<category>")
def category(category):
    return render_template("category.html", category=category)

# Reflection Route
@app.route("/<category>/<event>")
def reflection(category, event):
    return render_template("reflection.html", category=category, event=event)

if __name__ == "__main__":
    app.run(debug=True)
