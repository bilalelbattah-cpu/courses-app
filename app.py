
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Gestion des Courses", page_icon="🛒", layout="centered")

@st.cache_data
def load_reference(path: str):
    # Le fichier a des colonnes supplémentaires et deux premières lignes non utiles
    raw = pd.read_excel(path, skiprows=2, header=None)
    ref = raw.iloc[:, 1:4].copy()
    ref.columns = ["Catégorie", "Sous-catégorie", "Magasin"]
    # Nettoyage basique
    ref = ref.dropna(how="all")
    ref["Catégorie"] = ref["Catégorie"].astype(str).str.strip()
    ref["Sous-catégorie"] = ref["Sous-catégorie"].astype(str).str.strip()
    ref["Magasin"] = ref["Magasin"].astype(str).str.strip()
    return ref

REF = load_reference("grocerie.xlsx")

st.title("🛒 Gestion des Courses (MAD)")

# État: liste des achats
if "achats" not in st.session_state:
    st.session_state["achats"] = []

# Sélecteurs dynamiques
cats = sorted([c for c in REF["Catégorie"].dropna().unique() if c and c.lower() != "nan"])
cat = st.selectbox("Catégorie", cats, index=0 if cats else None)

ss = REF[REF["Catégorie"] == cat]["Sous-catégorie"].dropna().unique() if cat else []
sous_cat = st.selectbox("Sous-catégorie", sorted(ss) if len(ss) else [])

mags = REF["Magasin"].dropna().unique()
liste_magasins = sorted([m for m in mags if m and m.lower() != "nan"])
magasin = st.selectbox("Magasin", liste_magasins)

montant = st.number_input("Montant (Dirham - MAD)", min_value=0.0, step=0.5, format="%.2f")
d = st.date_input("Date", value=date.today())
note = st.text_input("Note (optionnel)", placeholder="ex: promo, bio, etc.")

col_btn1, col_btn2 = st.columns([1,1])
with col_btn1:
    if st.button("Ajouter l'achat"):
        if cat and sous_cat and magasin and montant > 0:
            st.session_state["achats"].append({
                "Date": pd.to_datetime(d),
                "Catégorie": cat,
                "Sous-catégorie": sous_cat,
                "Magasin": magasin,
                "Montant (DH)": float(montant),
                "Note": note.strip() or ""
            })
            st.success("✅ Achat ajouté")
        else:
            st.warning("Veuillez remplir tous les champs et un montant > 0.")

with col_btn2:
    if st.button("Tout effacer"):
        st.session_state["achats"] = []
        st.info("Historique vidé.")

# Historique
df = pd.DataFrame(st.session_state["achats"])
st.subheader("📋 Historique des achats")
if df.empty:
    st.caption("Aucun achat pour l'instant.")
else:
    st.dataframe(df, use_container_width=True)

    # Synthèse par mois
    st.subheader("📅 Dépenses mensuelles")
    df["_Mois"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)
    synth_mois = df.groupby("_Mois", as_index=False)["Montant (DH)"].sum().sort_values("_Mois")
    st.dataframe(synth_mois, use_container_width=True)
    st.bar_chart(data=synth_mois, x="_Mois", y="Montant (DH)")

    # Synthèse par catégorie
    st.subheader("📌 Dépenses par catégorie")
    synth_cat = df.groupby("Catégorie", as_index=False)["Montant (DH)"].sum().sort_values("Montant (DH)", ascending=False)
    st.dataframe(synth_cat, use_container_width=True)
    st.bar_chart(data=synth_cat, x="Catégorie", y="Montant (DH)")

    # Téléchargements
    st.subheader("💾 Exporter les données")
    csv = df.drop(columns=["_Mois"], errors="ignore").to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger CSV", data=csv, file_name="achats.csv", mime="text/csv")

st.markdown(\"\"\"\n---\n**Astuce mobile :** après déploiement sur Streamlit Cloud, ouvre l'URL sur ton smartphone et utilise **Ajouter à l'écran d'accueil** pour un accès rapide.\n\"\"\")    
