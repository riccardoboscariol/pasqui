import streamlit as st
import requests
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# Recupera le chiavi API e credenziali da Streamlit secrets
GEMINI_API_KEY = st.secrets["gembini"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Funzione per generare l'articolo con Gemini
def generate_article_gemini(keywords):
    prompt = f"Genera un articolo di alta qualità basato sulle parole chiave: {keywords}. Assicurati che l'articolo sia informativo, ben scritto e ottimizzato per SEO."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        return response.json().get("content", "Errore: Nessun testo generato dalla risposta.")
    else:
        st.error(f"Errore durante la generazione dell'articolo: {response.status_code} - {response.text}")
        return ""

# Funzione per pubblicare su WordPress
def publish_to_wordpress(title, content):
    try:
        # Crea la connessione al sito WordPress
        wp = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
        
        # Crea un nuovo post WordPress
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = "publish"  # Pubblica l'articolo immediatamente
        
        # Invia il post tramite la API XML-RPC
        wp.call(NewPost(post))
        st.success("Articolo pubblicato con successo!")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Streamlit UI
st.title("Generatore di articoli con Gemini AI")
keywords = st.text_input("Inserisci le parole chiave")

if st.button("Genera e Pubblica Articolo"):
    if keywords.strip():  # Verifica che le parole chiave non siano vuote
        st.info("Generazione dell'articolo in corso...")
        article_content = generate_article_gemini(keywords)
        if article_content:
            title = f"Articolo su {keywords.capitalize()}"
            publish_to_wordpress(title, article_content)
    else:
        st.warning("Inserisci delle parole chiave valide!")

