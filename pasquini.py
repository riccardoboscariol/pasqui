import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json
import time

# Configurazione API Claude
claude_api_key = st.secrets["claude"]["api_key"]

# Configurazione API Canva
canva_api_key = st.secrets["canva"]["api_key"]

# Configurazione WordPress
wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
wp_user = st.secrets["wordpress"]["username"]
wp_password = st.secrets["wordpress"]["password"]

# Funzione per creare un batch di richieste con Claude
def create_message_batch(prompt):
    url = "https://api.anthropic.com/v1/message_batches"
    headers = {
        "x-api-key": claude_api_key,
        "Content-Type": "application/json",
    }

    batch_data = {
        "requests": [
            {
                "custom_id": "article_generation_request",
                "params": {
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 4096,  # Numero maggiore di token per generare l'intera guida
                    "messages": [{"role": "user", "content": prompt}],
                },
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=batch_data)
        if response.status_code == 201:
            batch_info = response.json()
            st.success(f"Batch creato con ID: {batch_info['id']}")
            return batch_info["id"]
        else:
            st.error(f"Errore nella creazione del batch: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la creazione del batch: {e}")
        return None

# Funzione per monitorare lo stato di un batch
def monitor_batch(batch_id):
    url = f"https://api.anthropic.com/v1/message_batches/{batch_id}"
    headers = {
        "x-api-key": claude_api_key,
    }

    while True:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                batch_status = response.json()
                if batch_status["processing_status"] == "ended":
                    st.success("Batch completato!")
                    return batch_status.get("results_url")
                elif batch_status["processing_status"] == "in_progress":
                    st.info("Batch in elaborazione, attendere...")
                else:
                    st.error(f"Stato batch sconosciuto: {batch_status['processing_status']}")
                    return None
            else:
                st.error(f"Errore nel monitoraggio del batch: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            st.error(f"Errore durante il monitoraggio del batch: {e}")
            return None

        time.sleep(5)  # Attendi 5 secondi prima di riprovare

# Funzione per recuperare i risultati del batch
def retrieve_batch_results(results_url):
    try:
        response = requests.get(results_url)
        if response.status_code == 200:
            results = response.json()
            for result in results:
                if result["result"]["type"] == "succeeded":
                    return result["result"]["message"]["content"]
            st.error("Nessun risultato valido trovato nel batch.")
            return None
        else:
            st.error(f"Errore nel recupero dei risultati: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante il recupero dei risultati: {e}")
        return None

# Funzione per generare l'immagine con Canva API
def generate_image_canva():
    url = "https://api.canva.com/v1/images/generate"
    headers = {
        "Authorization": f"Bearer {canva_api_key}",
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
            return response.json().get("image_url")
        else:
            st.error(f"Errore nella generazione dell'immagine: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'immagine: {e}")
        return None

# Funzione per pubblicare l'articolo su WordPress
def publish_to_wordpress(title, content, image_url=None):
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
    }

    if image_url:
        post_data['featured_media'] = image_url

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
        prompt = (
            "Scrivi una guida di almeno 1000 parole come se fossi uno psicologo..."
            # Qui aggiungi il prompt completo
        )

        batch_id = create_message_batch(prompt)
        if batch_id:
            results_url = monitor_batch(batch_id)
            if results_url:
                guide_content = retrieve_batch_results(results_url)
                if guide_content:
                    st.subheader("Contenuto Generato:")
                    st.write(guide_content)

                    # Genera immagine
                    if st.button("Genera Immagine"):
                        image_url = generate_image_canva()
                        if image_url:
                            st.image(image_url, caption="Immagine Generata")

                    # Pubblica articolo
                    if st.button("Pubblica Articolo"):
                        title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
                        publish_to_wordpress(title, guide_content)

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()




