"""
POLARIN Zenodo Community Dataset Registration
Streamlit app to register datasets to the EU-POLARIN Zenodo community.
Project: POLARIN (https://eu-polarin.eu/)
Funding: https://cordis.europa.eu/project/id/101130949
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path

# ─── Configurazione pagina ───────────────────────────────────────────────────
st.set_page_config(
    page_title="POLARIN – Dataset Registration",
    page_icon="🧊",
    layout="centered",
)

# ─── Costanti ────────────────────────────────────────────────────────────────
ZENODO_API_URL     = "https://zenodo.org/api"
ZENODO_COMMUNITY   = "eu-polarin"
POLARIN_PROJECT    = "POLARIN – Polar Research Infrastructure Network"
POLARIN_URL        = "https://eu-polarin.eu/"
CORDIS_ID          = "101130949"
CORDIS_URL         = f"https://cordis.europa.eu/project/id/{CORDIS_ID}"
FUNDING_PROGRAM    = "European Union's Horizon Europe research and innovation programme"
FUNDING_GRANT      = "101130949"

# ─── Stili CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Header POLARIN */
    .polarin-header {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 0 24px 0;
        border-bottom: 2px solid #1a4f8a;
        margin-bottom: 28px;
    }
    .polarin-title { color: #1a4f8a; font-size: 1.6rem; font-weight: 700; }
    .polarin-subtitle { color: #555; font-size: 0.85rem; }

    /* Sezioni form */
    .section-title {
        font-size: 1rem;
        font-weight: 700;
        color: #1a4f8a;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid #cce0f5;
        padding-bottom: 4px;
        margin-top: 28px;
        margin-bottom: 12px;
    }

    /* Badge funding */
    .funding-badge {
        background: #eaf3fb;
        border-left: 4px solid #1a4f8a;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 0.82rem;
        color: #333;
        margin-bottom: 16px;
    }

    /* Success box */
    .success-box {
        background: #eafaf1;
        border: 1px solid #27ae60;
        border-radius: 6px;
        padding: 16px;
        color: #1e8449;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="polarin-header">
    <div>
        <div class="polarin-title">🧊 POLARIN</div>
        <div class="polarin-subtitle">Polar Research Infrastructure Network</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("## Dataset registration to the POLARIN Zenodo Community")

st.markdown(f"""
<div class="funding-badge">
    <b>Project:</b> <a href="{POLARIN_URL}" target="_blank">{POLARIN_PROJECT}</a><br>
    <b>Funding:</b> {FUNDING_PROGRAM} — Grant Agreement No. <a href="{CORDIS_URL}" target="_blank">{FUNDING_GRANT}</a>
</div>
""", unsafe_allow_html=True)

# ─── Zenodo Token ────────────────────────────────────────────────────────────
with st.expander("🔑 Zenodo API Token (required)", expanded=True):
    token_input = st.text_input(
        "Personal Access Token",
        type="password",
        placeholder="Incolla qui il tuo Zenodo token...",
        help="Vai su zenodo.org → Account → Applications → Personal access tokens. "
             "Scope richiesti: deposit:write, deposit:actions",
    )
    # Supporto anche secrets Streamlit
    ZENODO_TOKEN = token_input or st.secrets.get("ZENODO_TOKEN", "")

# ─── SEZIONE 1: DOI esistente o upload file ───────────────────────────────────
st.markdown('<div class="section-title">Does your dataset already have a DOI?</div>', unsafe_allow_html=True)

has_doi = st.radio(
    "Seleziona una opzione",
    options=["yes", "no"],
    label_visibility="collapsed",
    horizontal=True,
)

existing_doi  = None
uploaded_file = None

if has_doi == "yes":
    existing_doi = st.text_input("DOI", placeholder="10.5281/zenodo.XXXXXXX")
    st.info("ℹ️ Il record esistente verrà linkato alla community POLARIN tramite la Zenodo API.")
else:
    st.markdown("**Upload your dataset**")
    uploaded_file = st.file_uploader(
        "Drop your file here",
        type=None,
        label_visibility="collapsed",
        help="Formati accettati: qualsiasi. Consigliati: CSV, NetCDF, ZIP, PDF.",
    )

# ─── SEZIONE 2: Informazioni sull'utente ────────────────────────────────────
st.markdown('<div class="section-title">Information about the user</div>', unsafe_allow_html=True)

# Primo autore
col_name, col_orcid = st.columns([2, 2])
with col_name:
    author_name = st.text_input("Name", key="author_name_0", placeholder="Nome e Cognome")
with col_orcid:
    author_orcid = st.text_input("ORCID", key="author_orcid_0", placeholder="0000-0000-0000-0000")

# Collaboratori aggiuntivi
if "num_collaborators" not in st.session_state:
    st.session_state.num_collaborators = 0

if st.button("＋ Add another collaborator"):
    st.session_state.num_collaborators += 1

collaborators = []
for i in range(st.session_state.num_collaborators):
    st.markdown(f"*Collaboratore {i + 1}*")
    c1, c2 = st.columns([2, 2])
    with c1:
        cname  = st.text_input("Name", key=f"coll_name_{i}", placeholder="Nome e Cognome")
    with c2:
        corcid = st.text_input("ORCID", key=f"coll_orcid_{i}", placeholder="0000-0000-0000-0000")
    collaborators.append({"name": cname, "orcid": corcid})

# ─── SEZIONE 3: Informazioni sul progetto ───────────────────────────────────
st.markdown('<div class="section-title">Information about the project</div>', unsafe_allow_html=True)

project_name = st.text_input("Project's name", placeholder="es. POLARIN, MyArctic2024...")

# ─── SEZIONE 4: Descrizione della misura ────────────────────────────────────
st.markdown('<div class="section-title">Description of the measurement</div>', unsafe_allow_html=True)

description = st.text_area(
    "Describe how you collect the dataset",
    placeholder="Descri il metodo di raccolta, strumentazione usata, periodo...",
    height=100,
)

spatial_deployment = st.radio(
    "Specify the spatial deployment of the device",
    options=["Fixed", "Area", "Trajectory"],
    horizontal=True,
    label_visibility="visible",
)

# ─── SEZIONE 5: Metadati aggiuntivi ──────────────────────────────────────────
st.markdown('<div class="section-title">Additional metadata</div>', unsafe_allow_html=True)

col_title, col_license = st.columns([3, 2])
with col_title:
    record_title = st.text_input("Dataset title *", placeholder="Titolo del dataset su Zenodo")
with col_license:
    license_choice = st.selectbox(
        "License",
        options=["cc-by-4.0", "cc0-1.0", "cc-by-sa-4.0", "mit", "apache-2.0"],
        index=0,
    )

keywords_raw = st.text_input(
    "Keywords (comma-separated)",
    placeholder="polar, oceanography, temperature, Arctic...",
)
keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]

# Zona geografica
col_lat, col_lon = st.columns(2)
with col_lat:
    lat = st.number_input("Latitude (°N)", value=0.0, min_value=-90.0, max_value=90.0, step=0.01, format="%.4f")
with col_lon:
    lon = st.number_input("Longitude (°E)", value=0.0, min_value=-180.0, max_value=180.0, step=0.01, format="%.4f")

# ─── Funzioni Zenodo ─────────────────────────────────────────────────────────

def build_metadata(title, description_text, authors_list, spatial, proj, kw, lat_val, lon_val, lic):
    """Costruisce il dizionario metadati per InvenioRDM."""
    creators = []
    for a in authors_list:
        if not a.get("name"):
            continue
        creator = {"person_or_org": {"type": "personal", "name": a["name"]}}
        if a.get("orcid"):
            creator["person_or_org"]["identifiers"] = [
                {"scheme": "orcid", "identifier": a["orcid"]}
            ]
        creators.append(creator)

    desc_full = (
        f"{description_text}\n\n"
        f"Spatial deployment: {spatial}.\n"
        f"Coordinates (lat, lon): {lat_val:.4f}, {lon_val:.4f}.\n\n"
        f"Project: {proj or POLARIN_PROJECT}.\n"
        f"Funded by the {FUNDING_PROGRAM} under grant agreement No. {FUNDING_GRANT}."
    )

    metadata = {
        "title":        title,
        "description":  desc_full,
        "resource_type": {"id": "dataset"},
        "creators":     creators,
        "rights":       [{"id": lic}],
        "communities":  [{"id": ZENODO_COMMUNITY}],
        "funding": [
            {
                "funder": {
                    "name": "European Commission",
                    "scheme": "doi",
                    "identifier": "10.13039/501100000780",
                },
                "award": {
                    "title":      {"en": POLARIN_PROJECT},
                    "number":     FUNDING_GRANT,
                    "identifiers": [
                        {"scheme": "url", "identifier": CORDIS_URL}
                    ],
                },
            }
        ],
    }

    if kw:
        metadata["subjects"] = [{"subject": k} for k in kw]

    return metadata


def create_draft(token, metadata):
    """Step 1 – Crea un draft su Zenodo."""
    r = requests.post(
        f"{ZENODO_API_URL}/records",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json={"metadata": metadata},
    )
    r.raise_for_status()
    return r.json()


def upload_file_to_draft(token, record_id, file_bytes, filename):
    """Step 2 – Carica il file nel draft."""
    # Inizializza la lista file
    r = requests.post(
        f"{ZENODO_API_URL}/records/{record_id}/draft/files",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json=[{"key": filename}],
    )
    r.raise_for_status()

    # Upload contenuto
    r2 = requests.put(
        f"{ZENODO_API_URL}/records/{record_id}/draft/files/{filename}/content",
        headers={"Content-Type": "application/octet-stream", "Authorization": f"Bearer {token}"},
        data=file_bytes,
    )
    r2.raise_for_status()

    # Commit file
    r3 = requests.post(
        f"{ZENODO_API_URL}/records/{record_id}/draft/files/{filename}/commit",
        headers={"Authorization": f"Bearer {token}"},
    )
    r3.raise_for_status()
    return r3.json()


def publish_draft(token, record_id):
    """Step 3 – Pubblica il draft."""
    r = requests.post(
        f"{ZENODO_API_URL}/records/{record_id}/draft/actions/publish",
        headers={"Authorization": f"Bearer {token}"},
    )
    r.raise_for_status()
    return r.json()


def add_existing_doi_to_community(token, doi):
    """Tenta di aggiungere un record esistente alla community POLARIN."""
    # Cerca il record tramite DOI
    r = requests.get(
        f"{ZENODO_API_URL}/records",
        params={"q": f"doi:{doi}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    r.raise_for_status()
    hits = r.json().get("hits", {}).get("hits", [])
    if not hits:
        raise ValueError(f"Nessun record trovato per DOI: {doi}")
    record_id = hits[0]["id"]
    # Chiede inclusione nella community
    r2 = requests.post(
        f"{ZENODO_API_URL}/communities/{ZENODO_COMMUNITY}/records",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        json={"records": [{"id": str(record_id)}]},
    )
    r2.raise_for_status()
    return record_id


# ─── Bottone Submit ───────────────────────────────────────────────────────────
st.markdown("---")
submit = st.button("🚀 Register dataset to POLARIN community", type="primary", use_container_width=True)

if submit:
    # Validazione
    errors = []
    if not ZENODO_TOKEN:
        errors.append("Token Zenodo mancante.")
    if has_doi == "yes" and not existing_doi:
        errors.append("Inserisci il DOI del dataset esistente.")
    if has_doi == "no" and not uploaded_file:
        errors.append("Carica un file dataset.")
    if not author_name:
        errors.append("Inserisci almeno il nome del primo autore.")
    if has_doi == "no" and not record_title:
        errors.append("Inserisci il titolo del dataset.")
    if has_doi == "no" and not description:
        errors.append("Aggiungi una descrizione della misura.")

    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    # Lista autori
    all_authors = [{"name": author_name, "orcid": author_orcid}] + collaborators

    with st.spinner("Caricamento in corso su Zenodo..."):
        try:
            if has_doi == "yes":
                # ── Modalità DOI esistente ──
                record_id = add_existing_doi_to_community(ZENODO_TOKEN, existing_doi)
                st.markdown(f"""
                <div class="success-box">
                    ✅ <b>Record aggiunto alla community POLARIN!</b><br>
                    Record ID: <code>{record_id}</code><br>
                    <a href="https://zenodo.org/records/{record_id}" target="_blank">
                    Visualizza su Zenodo →</a>
                </div>
                """, unsafe_allow_html=True)

            else:
                # ── Modalità nuovo upload ──
                metadata = build_metadata(
                    title=record_title,
                    description_text=description,
                    authors_list=all_authors,
                    spatial=spatial_deployment,
                    proj=project_name,
                    kw=keywords,
                    lat_val=lat,
                    lon_val=lon,
                    lic=license_choice,
                )

                # Step 1 – Draft
                draft_info = create_draft(ZENODO_TOKEN, metadata)
                record_id  = draft_info["id"]
                st.info(f"📝 Draft creato (ID: {record_id})")

                # Step 2 – Upload file
                file_bytes = uploaded_file.read()
                upload_file_to_draft(ZENODO_TOKEN, record_id, file_bytes, uploaded_file.name)
                st.info(f"📂 File '{uploaded_file.name}' caricato.")

                # Step 3 – Pubblica
                published = publish_draft(ZENODO_TOKEN, record_id)
                doi_out   = published.get("doi", "n/a")

                st.markdown(f"""
                <div class="success-box">
                    ✅ <b>Dataset pubblicato nella community POLARIN!</b><br>
                    DOI: <code>{doi_out}</code><br>
                    Record ID: <code>{record_id}</code><br>
                    <a href="https://zenodo.org/records/{record_id}" target="_blank">
                    Visualizza su Zenodo →</a>
                </div>
                """, unsafe_allow_html=True)

                st.balloons()

        except requests.exceptions.HTTPError as e:
            st.error(f"❌ Errore HTTP Zenodo: {e.response.status_code} — {e.response.text}")
        except ValueError as e:
            st.error(f"❌ {e}")
        except Exception as e:
            st.error(f"❌ Errore inatteso: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<small>Powered by <a href='{POLARIN_URL}'>POLARIN</a> · "
    f"Grant Agreement No. <a href='{CORDIS_URL}'>{FUNDING_GRANT}</a> · "
    f"<a href='https://zenodo.org/communities/{ZENODO_COMMUNITY}'>Zenodo community</a></small>",
    unsafe_allow_html=True,
)
