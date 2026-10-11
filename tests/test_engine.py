import pandas as pd
from drought_engine import build_queries, canonical_url, classify, detect_region, relevance, risk_score, dedupe, enrich_dataframe

def test_queries():
    assert build_queries("Kekeringan",["irigasi"],"Jawa Tengah")==["Kekeringan Jawa Tengah","irigasi Jawa Tengah"]

def test_url():
    assert canonical_url("HTTPS://Example.com/a?utm_source=x#x")=="https://example.com/a"

def test_relevance():
    r={"Judul":"Kekeringan melanda Jawa Tengah","RingkasanAsli":"Irigasi kekurangan air","Sumber":"Test"}
    s,m=relevance(r,["kekeringan","irigasi"])
    assert s>=70 and "kekeringan" in m

def test_classify():
    assert classify("kekeringan menyebabkan gagal panen")== "Kekeringan" or classify("kekeringan menyebabkan gagal panen")=="Pertanian"

def test_region():
    assert "Jawa Tengah" in detect_region("Kekeringan di Jawa Tengah")

def test_risk():
    r={"Judul":"Darurat kekeringan dan gagal panen","RingkasanAsli":"","Skor":40}
    r["Skor Risiko"],r["Risiko"],r["Indikator Risiko"]=0,"",""
    # direct internal-compatible calculation
    from drought_engine import risk_score
    s,l,i=risk_score(r)
    assert l=="TINGGI"

def test_dedupe():
    rows=[{"URL":"https://x.com/a?q=1","Judul":"A"},{"URL":"https://x.com/a","Judul":"A"},{"URL":"https://x.com/b","Judul":"B"}]
    assert len(dedupe(rows))==2
