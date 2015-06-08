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

def taglink(tag):
    return Markup(r'<a class="btn btn-xs btn-success" href="/t/{0}">{0}</a>'.format(tag))
app.jinja_env.globals.update(taglink=taglink)
    


@app.route("/c/<symbol>")
def cacheit(symbol):
    sym = sm.get(symbol)
    result = sym.cache()
    tit = "Recaching Results"
    mac = sym.name + " was re-cached successfully!"
    nfo = Markup(result.html)
    return render_template('confirmation.html', msg_title=tit, msg_macro="", msg_info=nfo)

@app.route("/t/<tag>")
def tagged(tag):
    print tag
    name = False
    desc = False
    tags = True
    meta = False
    syms = sm.search(StringOnly=True)
    
    results = sm.search(tag, name=name, desc=desc, tags=tags, meta=meta, dolikelogic=False)
    if len(results) == 0:
        msg = "No Symbols Tagged {} Found".format(tag)
    else:
        msg = ""

    return render_template('home.html', msg=msg, symbols=syms, qry="", results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/q/", methods=['POST'])
def queried_browser():
    qry = request.form['qry']
    name = request.form.has_key('scname')
    desc = request.form.has_key('scdesc')
    tags = request.form.has_key('sctags')
    meta = request.form.has_key('scmeta')
    syms = sm.search(StringOnly=True)
    
    print syms
    if (len(qry) > 0) and (name or desc or tags or meta):
        results = sm.search(qry, name=name, desc=desc, tags=tags, meta=meta)
        msg = "No Results Found"
    else:
        results = []
        msg = "Must type something, and select either name, description, tags or meta."
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/")
def default_browser():
    qry = "Type here to search Trump"
    syms = sm.search(StringOnly=True)
    msg = "Type to Search"
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=[])        

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