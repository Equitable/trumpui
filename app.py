f = open("trumpui.log",'wb+')
f.write("pre flask import")
from flask import Flask, request, session, url_for, redirect, \
    render_template, abort, g, flash, _app_ctx_stack, make_response

import datetime as dt

f.write("pre string io import")

import cStringIO as cio

import sys

import pandas as pd

from trump.orm import SymbolManager

sm = SymbolManager()

from jinja2 import Markup


app = Flask(__name__)

f.write("done making flask object")


def symurl(sym):
    return Markup(r"<a href=/s/{0}>{0}</a>".format(sym))
app.jinja_env.globals.update(symurl=symurl)

def taglink(tag):
    return Markup(r'<a class="btn btn-xs btn-success" href="/t/{0}">{0}</a>'.format(tag))
app.jinja_env.globals.update(taglink=taglink)

def cleanmaxmin(symbol):
    mxmn = symbol._max_min()
    
    def tostr(obj):
        if isinstance(obj, dt.datetime):
            return obj.strftime("%Y-%m-%d")
        else:
            return str(obj)
     
    return Markup(" to ".join([tostr(mm) for mm in mxmn]))
app.jinja_env.globals.update(cleanmaxmin=cleanmaxmin)   


@app.route("/about")
def about():
    eng = sm.eng
    mac = "Currently Connected to..."
    info = str(eng.dialect) + Markup( "<br>" + str(eng.name) + "<br>" + str(eng))
    return render_template('about.html', msg_title="About Trump", msg_macro=mac, msg_info=info)

@app.route("/raiseanerror")
def raiseanerror():
    somedict = {'jeff' : 'wins', 'trump': 'rock'}
    
    print somedict
    
    raise Exception("Nothing , jeff put this here")

@app.route("/chart/<symbol>")
@app.route("/chart/<symbol>/<freq>/<opt>/<kind>")
def chart(symbol,freq=None,opt=None,kind=None):
    sym = sm.get(symbol)
    df = sym.df
    
    f = cio.StringIO()
   
    if freq:
        df = df.asfreq(freq, method='ffill')
    
    if opt == 'pct':
        df = df.pct_change(1)
    
    if kind:
        ax = df.plot(kind=kind, title=sym.description, legend=False)
    else:
        ax = df.plot(title=sym.description, legend=False)
        
    ax.set_xlabel(sym.name)
    ax.set_ylabel(sym.units)
        
    
    fig = ax.get_figure()
    
    fig.savefig(f, format='png')
    
    header = {'Content-type' : 'image/png'}
    f.seek(0)
    data = f.read()
    
    return data, 200, header

@app.route("/export/<ext>/<symbol>")
@app.route("/export/<ext>/<symbol>/<freq>")
def export(ext, symbol, freq=None):
    
    sym = sm.get(symbol)
    
    f = cio.StringIO()
    
    df = sym.df
    
    if freq:
        df = df.asfreq(freq, method='ffill')
    
    if ext == 'csv':
        sym.df.to_csv(f, sep=',', header=True)
        header = {'Content-Disposition' : "attachment; filename=" + sym.name + ".csv"}
        f.seek(0)
        data = f.read()
        return data, 200, header    
        
    elif ext == 'xlsx':
        fn = sym.name + ".xlsx"
        wrtr = pd.ExcelWriter(fn, engine='xlsxwriter')
        wrtr.book.filename = f
        df.to_excel(wrtr, sheet_name=sym.name)
        wrtr.save()
        header = {'Content-Disposition' : "attachment; filename=" + sym.name + ".xls"}
        f.seek(0)
        data = f.read()
        return data, 200, header

@app.route("/orfs/<symbol>")
def orfs(symbol):
    sym = sm.get(symbol)
    data = sym._all_datatable_data()
    data = [(i,row) for i,row in enumerate(data)]
    return render_template('symbol_orfs.html', symbol=sym, data=data)

@app.route("/c/<symbol>")
def c(symbol):
    """ Cache a symbol """
    sym = sm.get(symbol)
    try:
        result = sym.cache()
        tit = "Recaching Results"
        mac = sym.name + " was (likely) re-cached successfully!"
        nfo = Markup(result.html)
    except:
        tit = "Problem!"
        mac = "Caching of {} (likely) failed".format(sym.name)
        nfo = "Check your inbox, server logs, trump logs for more info"
        # TODO lots of work here...with the traceback
    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo)

@app.route("/t/<tag>")
def t(tag):
    """ Tag Searching..."""
    syms = sm.search(stronly=True)
    
    results = sm.search(tag, tags=True, dolikelogic=False)
    if len(results) == 0:
        msg = "No Symbols Tagged {} Found".format(tag)
    else:
        msg = ""
    return render_template('home.html', msg=msg, symbols=syms, qry="", results=results, name=False, desc=False, tags=True, meta=False)

@app.route("/q/", methods=['POST'])
def queried_browser():
    """ Query browser """
    qry = request.form['qry']
    name = request.form.has_key('scname')
    desc = request.form.has_key('scdesc')
    tags = request.form.has_key('sctags')
    meta = request.form.has_key('scmeta')
    syms = sm.search(stronly=True)
    
    print syms
    if (len(qry) > 0) and (name or desc or tags or meta):
        results = sm.search(qry, name=name, desc=desc, tags=tags, meta=meta)
        msg = "No Results Found"
    else:
        results = []
        msg = "Must type something, and select either name, description, tags or meta."
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=results, name=name, desc=desc, tags=tags, meta=meta)

@app.route("/")
def home():
    qry = "Type here to search Trump"
    syms = sm.search(stronly=True)
    msg = "Type to Search"
    return render_template('home.html', msg=msg, symbols=syms, qry=qry, results=[])        

@app.route("/orfssaved/", methods=['POST'])
def orfssaved():
    usrinput = request.form
    
    comment = usrinput['comment']
    
    # Some major thinking needs to be done here...to implement this in a robust way, for all data and index 
    # types
    
    def isgood(v):
        return len(v) > 0
    def togood(v):
        return float(v)
    
    ors = {int(key[2:]) : togood(value) for key,value in usrinput.iteritems() if isgood(value) and key[:2] == 'or'}
    fss = {int(key[2:]) : togood(value) for key,value in usrinput.iteritems() if isgood(value) and key[:2] == 'fs'}
    
    return "{} {} {}".format(str(ors),str(fss),comment)

@app.route("/installtrump")
def installtrump():
    from trump import SetupTrump
    SetupTrump()
    return "Trump likely installed correctly"

@app.route("/installsymbols")
def installsymbols():
    import setupsymbols
    return "Likedly done creating a bunch of symbols"

@app.route("/s/<symbol>")
def s(symbol):
    """ Symbol Page """
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

@app.route("/delete/<symbol>")
def delete(symbol):
    """ Symbol Page """
    sym = sm.get(symbol)
    name = sym.name
    sm.delete(sym)
    
    tit = "Deleted " + name
    mac = "Deletion of the symbol was successful..."
    nfo = "...Using SymbolManager.delete()"
    # TODO check to make sure it's actually deleted
    # Plus, some likely GitHub Issue
    return render_template('confirmation.html', msg_title=tit, msg_macro=mac, msg_info=nfo)

f.write("\n My name is {}".format(__name__))


if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler

    fh = RotatingFileHandler("trumpuisite.log", 'a')
    fh.setLevel(logging.WARNING)
    app.logger.addHandler(fh)

f.write("\I must have figured out how to handle")

if __name__ == "__main__":
    f.write("\n we shouldn't get here")
    if len(sys.argv) > 1:
        app.run(debug=True)
    else:
        app.run('0.0.0.0')

f.write("\n all done!")
f.close()
