from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack

from jinja2 import Markup

app = Flask(__name__)
def symurl(sym):
    return Markup(r"<a href=/s/{0}>{0}</a>".format(sym)) 
app.jinja_env.globals.update(symurl=symurl)

@app.route("/")
def hello():
    with app.test_request_context():
        s = url_for('search')
    syms = ['AAA', 'BBB', 'CCC']
    return render_template('home.html',symbols=syms) + s

@app.route("/search")
def search():
    return "Search, Trump."

@app.route("/s/<symbol>")
def symbol_page(symbol):
    return render_template('symbol_page.html',symbol=symbol)

if __name__ == "__main__":
    app.run(debug=True)