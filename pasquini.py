import streamlit as st
from anthropic import Anthropic
from wordpress_xmlrpc import Client as WPClient, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
import requests  # Assicurati di importare requests per interagire con l'API di Canva

# Recupera le informazioni dalle secrets di Streamlit
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Controllo per la chiave API di Canva nelle secrets
if "canva" in st.secrets and "api_key" in st.secrets["canva"]:
    CANVA_API_KEY = st.secrets["canva"]["api_key"]
else:
    st.error("Chiave API di Canva non trovata nelle secrets.")
    CANVA_API_KEY = None  # Imposta a None se non trovata

# Inizializza il client di Claude
claude_client = Anthropic(api_key=CLAUDE_API_KEY)

# Funzione per generare l'articolo con Claude AI utilizzando Messages API
def generate_article_claude():
    prompt = (
        "Scrivi una guida di almeno 1000 parole come se fossi uno psicologo con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di dimensione maggiore) "
        "per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour. "
        "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici e che devono rivolgersi sempre a professionisti. "
        "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante. "
        "Inizialmente non devi scrivere ecco a te il contenuto. Parti subito con la guida."
    )

    try:
        # Usa la Messages API per generare il contenuto
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",  # Modello corretto
            max_tokens=1024,
            system="You are a helpful and creative assistant.",  # Parametro top-level
            messages=[{"role": "user", "content": prompt}],
        )

        # Accedi al contenuto generato
        return response["completion"].strip()
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per estrarre un titolo accattivante dal contenuto generato
def extract_title(content):
    sentences = content.split("\n")
    title_candidates = [s.strip() for s in sentences if s.strip()]
    if title_candidates:
        return title_candidates[0]
    return "Titolo Accattivante per la Guida Psicologica"

# Funzione per applicare la formattazione HTML
def format_content(content):
    lines = content.split("\n")
    formatted_lines = []
    for line in lines:
        if line.startswith("# "):  # Titolo principale
            formatted_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("## "):  # Sottotitolo
            formatted_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):  # Sottosottotitolo
            formatted_lines.append(f"<h3>{line[4:]}</h3>")
        else:
            formatted_lines.append(f"<p>{line}</p>")
    return "\n".join(formatted_lines)

# Funzione per pubblicare su WordPress
def publish_to_wordpress(title, content):
    if not content.strip():
        st.error("Errore: Il contenuto dell'articolo è vuoto. Verifica la generazione dell'articolo.")
        return

    try:
        wp = WPClient(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = "publish"
        wp.call(NewPost(post))
        st.success("Articolo pubblicato con successo!")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Funzione per generare un'immagine tramite l'API di Canva
def generate_image_canva(content):
    if CANVA_API_KEY is None:
        st.warning("Impossibile generare un'immagine, chiave API di Canva non disponibile.")
        return None

    try:
        # Usa l'API di Canva per generare un'immagine in base al contenuto
        canva_api_url = "https://api.canva.com/v1/images/generate"  # URL API di Canva (è solo un esempio)
        headers = {"Authorization": f"Bearer {CANVA_API_KEY}"}
        data = {"content": content}
        
        # Richiesta POST per generare l'immagine
        response = requests.post(canva_api_url, headers=headers, data=data)
        
        if response.status_code == 200:
            image_url = response.json().get("image_url")  # URL dell'immagine generata
            return image_url
        else:
            st.error("Errore durante la generazione dell'immagine con Canva.")
            return None
    except Exception as e:
        st.error(f"Errore nell'interazione con l'API di Canva: {e}")
        return None

# Streamlit UI
st.title("Generatore di Guide con Claude AI")

if st.button("Genera e Pubblica Guida"):
    st.info("Generazione della guida in corso...")
    guide_content = generate_article_claude()
    if guide_content:
        st.write("Contenuto generato:", guide_content)  # Debug
        formatted_content = format_content(guide_content)
        title = extract_title(guide_content)
        publish_to_wordpress(title, formatted_content)

        # Genera l'immagine e mostra l'URL dell'immagine
        image_url = generate_image_canva(guide_content)
        if image_url:
            st.image(image_url, caption="Immagine generata da Canva")



