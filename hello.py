from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack

import pandas as pd

dw = pd.get_option('display.width')
from trump.orm import SymbolManager

sm = SymbolManager()

from jinja2 import Markup

app = Flask(__name__)
def symurl(sym):
    return Markup(r"<a href=/s/{0}>{0}</a>".format(sym)) 
app.jinja_env.globals.update(symurl=symurl)

@app.route("/q/", methods=['POST'])
def queried_browser():
    qry = request.form['qry']
    syms = sm.list_symbols()
    results = sm.list_symbols(False)
    return render_template('home.html', symbols=syms, qry=qry, results=results)

@app.route("/")
def default_browser():
    qry = "Type here to search Trump"
    syms = sm.list_symbols()
    return render_template('home.html', symbols=syms, qry=qry, results=[])        

@app.route("/s/<symbol>")
def symbol_page(symbol):
    sym = sm.get(symbol)
    metaattr = [meta.attr for meta in sym.meta]
    metaattr.sort()
    S = sym.df[sym.name]
    S.name = None
    ind = str(type(S.index)).split("'")[1]
    lind = len(S)
    
    tmp = str(S.tail(4))
    tmp = tmp.split("dtype")[0]
    tailhtml = Markup(tmp)
    
    dtype =  str(S.dtype)
    return render_template('symbol_page.html', symbol=sym, sdf=S, dtype=dtype, ind=ind,lind=lind, sdfhtml=tailhtml, metaattr=metaattr)

if __name__ == "__main__":
    app.run(debug=True)