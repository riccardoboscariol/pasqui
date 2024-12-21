import streamlit as st
import requests
import os

# Carica credenziali da variabili d'ambiente
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "INSERISCI_LA_TUA_API_KEY")
WORDPRESS_URL = os.getenv("WORDPRESS_URL", "https://tuo-blog.com")
WORDPRESS_USER = os.getenv("WORDPRESS_USER", "Richi")
WORDPRESS_PASSWORD = os.getenv("WORDPRESS_PASSWORD", "cazzone33082!")

# Funzione per generare l'articolo con Gemini
def generate_article_gemini(keywords):
    prompt = f"""
    Genera un articolo di alta qualità basato sulle parole chiave: {keywords}.
    Assicurati che l'articolo sia informativo, ben scritto e adatto a un pubblico ampio.
    Includi uno stile professionale e ottimizza per SEO.
    """
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "prompt": prompt,
        "max_tokens": 2000,
        "temperature": 0.7,  # Creatività moderata
        "top_p": 0.9  # Riduce le risposte incoerenti
    }
    try:
        response = requests.post(
            "https://gemini.googleapis.com/v1beta/models/text:generate",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            return response.json().get("text", "Errore: Nessun testo generato dalla risposta.")
        else:
            st.error(f"Errore durante la generazione dell'articolo: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        st.error(f"Errore durante la comunicazione con l'API Gemini: {e}")
        return ""

# Funzione per pubblicare su WordPress usando REST API
def publish_to_wordpress(title, content):
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
    headers = {
        "Authorization": f"Basic {requests.auth._basic_auth_str(WORDPRESS_USER, WORDPRESS_PASSWORD)}",
        "Content-Type": "application/json"
    }
    data = {
        "title": title,
        "content": content,
        "status": "publish"  # Pubblica immediatamente
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            st.success("Articolo pubblicato con successo!")
        else:
            st.error(f"Errore durante la pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore durante la comunicazione con WordPress: {e}")

# Interfaccia Streamlit
st.title("Generatore di articoli con Gemini AI")
keywords = st.text_input("Inserisci le parole chiave per l'articolo")

if st.button("Genera e Pubblica Articolo"):
    if keywords.strip():
        st.info("Generazione dell'articolo in corso...")
        article_content = generate_article_gemini(keywords)
        if article_content:
            title = f"Articolo su {keywords.capitalize()}"
            publish_to_wordpress(title, article_content)
    else:
        st.warning("Inserisci delle parole chiave valide!")

