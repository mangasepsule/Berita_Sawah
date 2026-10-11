from __future__ import annotations
import html, re, unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus, urlsplit, urlunsplit

import feedparser
import pandas as pd
import requests
from dateutil import parser as date_parser

UA = "DroughtEarlyWarning/3.1 (public-feed-collector)"
TIMEOUT = 15

DEFAULT_FEEDS = {
    "Google News - Kekeringan":
        "https://news.google.com/rss/search?q=kekeringan&hl=id&gl=ID&ceid=ID:id",
    "Google News - Krisis Air":
        "https://news.google.com/rss/search?q=%22krisis%20air%22&hl=id&gl=ID&ceid=ID:id",
    "Google News - Irigasi":
        "https://news.google.com/rss/search?q=irigasi%20kekeringan&hl=id&gl=ID&ceid=ID:id",
    "Google News - El Nino":
        "https://news.google.com/rss/search?q=El%20Nino%20kekeringan&hl=id&gl=ID&ceid=ID:id",
}

TOPICS = {
    "Kekeringan": ["kekeringan","drought","kemarau","dry spell"],
    "Krisis Air": ["krisis air","kelangkaan air","kekurangan air","defisit air","water scarcity"],
    "Irigasi": ["irigasi","air irigasi","debit irigasi","saluran irigasi"],
    "Pertanian": ["sawah","padi","petani","pertanian","gagal panen","puso","tanaman"],
    "Air Bersih": ["air bersih","air minum","sumur","sumur mengering","mata air mengering"],
    "Waduk & Embung": ["waduk","embung","reservoir","tampungan","waduk mengering","embung mengering"],
    "Iklim": ["el nino","el-nino","enso","curah hujan","iklim","hujan"],
    "Kebijakan": ["status siaga","status darurat","bantuan air","tanggap darurat","kebijakan"],
}

RISK_TERMS = {
    "Kekeringan parah": ["kekeringan parah","kekeringan ekstrem","kekeringan berat"],
    "Defisit air": ["defisit air","debit kritis","debit menurun","kekurangan air"],
    "Air bersih": ["krisis air bersih","air bersih sulit","sumur mengering","mata air mengering"],
    "Pertanian": ["gagal panen","puso","sawah kering","tanaman mati"],
    "Irigasi": ["irigasi berhenti","air irigasi tidak tersedia","debit irigasi kritis"],
    "Waduk/embung": ["waduk kritis","waduk mengering","embung mengering"],
    "Darurat": ["darurat kekeringan","tanggap darurat","status darurat","evakuasi"],
}

REGIONS = [
    "Jawa Tengah","Jawa Timur","Jawa Barat","DI Yogyakarta","Yogyakarta",
    "Bengawan Solo","Wonogiri","Wonogiri","Sukoharjo","Klaten","Boyolali",
    "Sragen","Grobogan","Blora","Rembang","Pati","Cilacap","Karanganyar",
    "Gunungkidul","Sleman","Bantul","Pacitan","Ngawi","Madiun","Nganjuk",
    "Kediri","Jakarta","Sumatera","Kalimantan","Sulawesi","Bali","Indonesia"
]

def clean(x):
    x = html.unescape(str(x or ""))
    x = unicodedata.normalize("NFKD", x)
    x = "".join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r"<[^>]+>", " ", x)
    return re.sub(r"\s+", " ", x).strip().lower()

def strip_html(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(str(x or "")))).strip()

def build_queries(theme, keywords, region):
    vals = ([theme.strip()] if theme.strip() else []) + [k.strip() for k in keywords if k.strip()]
    vals = list(dict.fromkeys(vals))
    if region.strip():
        vals = [f"{v} {region.strip()}" for v in vals]
    return vals

def gnews(q):
    return "https://news.google.com/rss/search?" + f"q={quote_plus(q)}&hl=id&gl=ID&ceid=ID:id"

def parse_dt(e):
    for field in ("published","updated","created"):
        if e.get(field):
            try:
                d = date_parser.parse(e[field])
                return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)
            except (ValueError,TypeError,OverflowError):
                pass
    return None

def canonical_url(url):
    try:
        p=urlsplit(url.strip())
        return urlunsplit((p.scheme.lower(),p.netloc.lower(),p.path.rstrip("/"),"",""))
    except Exception:
        return url.strip().lower()

def parse_custom_feed(item, index):
    """Accept either a URL or 'Nama Sumber | URL RSS' from the UI."""
    item = str(item or "").strip()
    if "|" in item:
        name, url = item.split("|", 1)
        name, url = name.strip(), url.strip()
        if name and url:
            return name, url
    return f"RSS Custom {index}", item


def infer_source_type(name, url):
    text = (str(name) + " " + str(url)).lower()
    if "youtube.com/feeds/videos.xml" in text or "youtube.com" in text:
        return "YouTube publik"
    if "instagram.com" in text:
        return "Instagram publik/terindeks"
    if "facebook.com" in text or "fb.watch" in text:
        return "Facebook publik"
    if "x.com" in text or "twitter.com" in text:
        return "X publik"
    if "news.google.com" in text or "google news" in text:
        return "Berita terindeks"
    return "Feed publik"


def fetch(url, name):
    try:
        r=requests.get(url,headers={"User-Agent":UA},timeout=TIMEOUT,allow_redirects=True)
        r.raise_for_status()
        if len(r.content)>8_000_000:
            return [], f"{name}: feed terlalu besar"
        f=feedparser.parse(r.content)
        if not f.entries and getattr(f,"bozo",False):
            return [], f"{name}: RSS tidak valid"
        rows=[]
        for e in f.entries:
            title=strip_html(e.get("title",""))
            link=str(e.get("link","")).strip()
            if not title or not link: continue
            source=name
            if e.get("source") and hasattr(e["source"],"get"):
                source=e["source"].get("title",source)
            rows.append({
                "TanggalUTC":parse_dt(e),
                "Judul":title,
                "RingkasanAsli":strip_html(e.get("summary",e.get("description","")))[:1200],
                "Sumber":source,
                "TipeSumber":infer_source_type(name, url),
                "URL":link
            })
        return rows,None
    except requests.RequestException as ex:
        return [],f"{name}: {ex.__class__.__name__}"
    except Exception as ex:
        return [],f"{name}: {ex.__class__.__name__}"

def relevance(row, keywords):
    t=clean(row["Judul"]); s=clean(row["RingkasanAsli"])
    score=0; matched=[]
    for kw in keywords:
        k=clean(kw)
        if not k: continue
        hit=False
        if k in t: score+=35; hit=True
        if k in s: score+=15; hit=True
        if hit: matched.append(k)
    score += min(20,5*len(set(matched)))
    return min(score,100),list(dict.fromkeys(matched))

def classify(text):
    t=clean(text)
    scores={k:sum(v in t for v in terms) for k,terms in TOPICS.items()}
    best=max(scores,key=scores.get)
    return best if scores[best] else "Lainnya"

def detect_region(text):
    t=clean(text)
    hits=[]
    for r in REGIONS:
        if clean(r) in t and r not in hits:
            hits.append(r)
    return ", ".join(hits[:5]) if hits else "Tidak terdeteksi"

def risk_score(row):
    text=clean(row["Judul"]+" "+row["RingkasanAsli"])
    score=int(row["Skor"])
    indicators={}
    for name,terms in RISK_TERMS.items():
        n=sum(1 for term in terms if term in text)
        if n: indicators[name]=n
    risk=min(100, score + min(45, sum(indicators.values())*12))
    if risk>=70: level="TINGGI"
    elif risk>=45: level="SEDANG"
    else: level="RENDAH"
    return risk,level,indicators

def dedupe(rows):
    out=[]; urls=set(); titles=set()
    for r in rows:
        u=canonical_url(r["URL"]); t=clean(r["Judul"])
        if u in urls or t in titles: continue
        urls.add(u); titles.add(t); out.append(r)
    return out

def search_drought_news(queries, keywords, feeds, custom_feeds, days, min_score, max_results):
    cutoff=datetime.now(timezone.utc)-timedelta(days=days)
    jobs=[(f"Google News: {q}",gnews(q)) for q in queries]
    jobs.extend(feeds.items())
    for i, item in enumerate(custom_feeds, 1):
        name, url = parse_custom_feed(item, i)
        if url:
            jobs.append((name, url))
    rows=[]; errors=[]
    for name,url in jobs:
        got,err=fetch(url,name)
        if err: errors.append(err)
        for r in got:
            if r["TanggalUTC"] and r["TanggalUTC"]<cutoff: continue
            sc,match=relevance(r,keywords)
            if sc<min_score: continue
            r["Skor"]=sc; r["Kata Kunci"]=", ".join(match)
            r["Subtema"]=classify(r["Judul"]+" "+r["RingkasanAsli"])
            r["Wilayah"]=detect_region(r["Judul"]+" "+r["RingkasanAsli"])
            rs,level,ind=risk_score(r); r["Skor Risiko"]=rs; r["Risiko"]=level
            r["Indikator Risiko"]="; ".join(ind.keys())
            rows.append(r)
    rows=dedupe(rows)
    rows.sort(key=lambda x:(x["Skor Risiko"],x["TanggalUTC"] or datetime.min.replace(tzinfo=timezone.utc)),reverse=True)
    return rows[:max_results],errors

def enrich_dataframe(rows):
    data=[]
    for r in rows:
        dt=r["TanggalUTC"]
        data.append({
            "Tanggal":dt.astimezone().strftime("%Y-%m-%d %H:%M") if dt else "",
            "Risiko":r["Risiko"],"Skor Risiko":r["Skor Risiko"],"Skor":r["Skor"],
            "Subtema":r["Subtema"],"Wilayah":r["Wilayah"],"Tipe Sumber":r["TipeSumber"],
            "Judul":r["Judul"],"Sumber":r["Sumber"],"Kata Kunci":r["Kata Kunci"],
            "Indikator Risiko":r["Indikator Risiko"],
            "Ringkasan":r["RingkasanAsli"][:500],"URL":r["URL"]
        })
    return pd.DataFrame(data)

def risk_summary(df):
    if df.empty:
        return {"risk_score":0,"dominant_topic":"-","indicators":{}}
    topic=df["Subtema"].mode().iat[0] if not df["Subtema"].mode().empty else "-"
    inds={}
    for text in df["Indikator Risiko"].fillna(""):
        for x in [v.strip() for v in text.split(";") if v.strip()]:
            inds[x]=inds.get(x,0)+1
    return {
        "risk_score":float(df["Skor Risiko"].mean()),
        "dominant_topic":topic,
        "indicators":dict(sorted(inds.items(),key=lambda x:x[1],reverse=True))
    }
