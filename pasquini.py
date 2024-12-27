import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json

# Configurazione di Claude
claude_api_key = st.secrets["claude"]["api_key"]  # La chiave API viene letta dai segreti

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
        # Modificato per includere l'header 'anthropic-version'
        response = requests.post(
            "https://api.anthropic.com/v1/messages",  # Endpoint corretto per i messaggi
            headers={
                "x-api-key": claude_api_key,  # Chiave API di Claude (header corretto)
                "anthropic-version": "2023-06-01",  # Versione dell'API di Claude
                "Content-Type": "application/json",
            },
            json={
                "model": "claude-3-5-sonnet-20241022",  # Modello corretto
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
            },
        )

        if response.status_code == 200:
            response_json = response.json()
            return response_json.get("completion", "").strip()  # Estrai il testo generato
        else:
            st.error(f"Errore nella risposta di Claude: {response.status_code} - {response.text}")
            return None  # Restituisce None in caso di errore
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None  # Restituisce None in caso di eccezione

# Funzione per generare un'immagine con Canva API
def generate_image_canva():
    url = "https://api.canva.com/v1/images/generate"  # Endpoint di generazione immagine
    headers = {
        "Authorization": f"Bearer {st.secrets['canva']['api_key']}",
        "Content-Type": "application/json",
    }

    data = {
        "template_id": "TEMPLATE_ID",  # Sostituisci con un template ID valido di Canva
        "variables": {
            "title": "Guida Psicologica",
            "content": "Immagine generata tramite l'API di Canva per l'articolo."
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            image_url = response.json().get("image_url")
            st.success("Immagine generata con successo!")
            return image_url
        else:
            st.error(f"Errore nella generazione dell'immagine: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'immagine: {e}")
        return None

# Funzione per pubblicare l'articolo su WordPress
def publish_to_wordpress(title, content, image_url=None):
    wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
    }

    if image_url:
        post_data['featured_media'] = image_url  # Usa l'URL dell'immagine come copertura

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
    st.title("Generatore di Articoli con Claude AI")

    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")
        # Genera il contenuto tramite Claude AI
        guide_content = generate_article_claude()

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Pulsante per generare l'immagine con Canva
            image_url = None
            if st.button("Genera Immagine per Articolo"):
                image_url = generate_image_canva()
                if image_url:
                    st.image(image_url, caption="Immagine Generata")

            # Pulsante per pubblicare l'articolo
            if st.button("Pubblica Articolo"):
                title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
                publish_to_wordpress(title, guide_content, image_url)
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


