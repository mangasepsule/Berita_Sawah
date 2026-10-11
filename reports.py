import io
import pandas as pd

def make_excel(df):
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine="openpyxl") as w:
        df.to_excel(w,index=False,sheet_name="Intelligence")
        df["Subtema"].value_counts().rename_axis("Subtema").reset_index(name="Jumlah").to_excel(w,index=False,sheet_name="Subtema")
        df["Risiko"].value_counts().rename_axis("Risiko").reset_index(name="Jumlah").to_excel(w,index=False,sheet_name="Risiko")
        df["Wilayah"].value_counts().rename_axis("Wilayah").reset_index(name="Jumlah").to_excel(w,index=False,sheet_name="Wilayah")
        df["Tipe Sumber"].value_counts().rename_axis("Tipe Sumber").reset_index(name="Jumlah").to_excel(w,index=False,sheet_name="Sumber")
        ws=w.book["Intelligence"]; ws.freeze_panes="A2"
        for col in ws.columns:
            letter=col[0].column_letter
            width=min(max([len(str(x.value or "")) for x in col[:100]]+[12])+2,60)
            ws.column_dimensions[letter].width=width
    return out.getvalue()
