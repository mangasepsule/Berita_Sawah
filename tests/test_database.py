import pandas as pd
import database

def test_database(tmp_path,monkeypatch):
    monkeypatch.setattr(database,"DB",tmp_path/"d.db")
    database.save_run(pd.DataFrame({"Skor Risiko":[80,60]}),"Kekeringan","Jawa Tengah")
    x=database.load_history()
    assert len(x)==1 and x.iloc[0]["Konten"]==2
