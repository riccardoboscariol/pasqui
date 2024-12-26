import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json

# Funzione per generare l'articolo con Claude AI
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
        response = requests.post(
            "https://api.anthropic.com/v1/complete",  # Endpoint corretto
            headers={
                "x-api-key": st.secrets["claude"]["api_key"],  # Chiave API dai segreti
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "model": "claude-2",  # Specifica il modello corretto
                "max_tokens_to_sample": 1024,
                "stop_sequences": ["\n\nHuman:"],  # Personalizza le sequenze di stop se necessario
            },
        )

        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("completion", "").strip()  # Estrai il testo generato
        else:
            st.error(f"Errore nella risposta di Claude: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per generare immagini con Canva
def generate_image_canva(description):
    try:
        response = requests.post(
            "https://api.canva.com/v1/generate-image",  # Endpoint di Canva API
            headers={
                "Authorization": f"Bearer {st.secrets['canva']['api_key']}",
                "Content-Type": "application/json",
            },
            json={
                "description": description,
                "size": "1024x1024",  # Dimensioni immagine
            },
        )

        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("image_url", "")  # Restituisce l'URL dell'immagine generata
        else:
            st.error(f"Errore nella risposta di Canva: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        st.error(f"Errore durante la generazione dell'immagine: {e}")
        return ""

# Funzione per pubblicare l'articolo su WordPress
def publish_to_wordpress(title, content, image_url):
    wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    # Prepara i dati per la richiesta
    post_data = {
        'title': title,
        'content': content + f'<img src="{image_url}" alt="Immagine generata">',  # Aggiungi immagine all'articolo
        'status': 'publish'  # Può essere 'draft' o 'publish'
    }

    try:
        response = requests.post(wp_url, json=post_data, auth=wp_auth)

        if response.status_code == 201:
            st.success(f"Articolo '{title}' pubblicato con successo!")
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore nella pubblicazione su WordPress: {e}")

# Streamlit UI per la generazione e pubblicazione dell'articolo
def main():
    st.title("Generatore di Articoli e Immagini con Claude AI e Canva")

    # Generazione articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")
        guide_content = generate_article_claude()

        if guide_content:
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Suggerisci un titolo automaticamente
            suggested_title = guide_content.split("\n")[0]  # Prima riga del contenuto generato
            title = st.text_input("Titolo dell'articolo:", value=suggested_title)

            # Generazione immagine
            description = st.text_input("Descrizione per l'immagine:")
            if st.button("Genera Immagine"):
                image_url = generate_image_canva(description)

                if image_url:
                    st.image(image_url, caption="Immagine Generata")
                    st.write(f"URL Immagine: {image_url}")

            # Pubblicazione articolo
            if st.button("Pubblica Articolo"):
                if not title.strip():
                    st.error("Il titolo dell'articolo non può essere vuoto!")
                else:
                    publish_to_wordpress(title, guide_content, image_url)

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()





