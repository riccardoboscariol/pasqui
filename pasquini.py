import streamlit as st
import requests

# Configurazione API Claude
claude_api_key = st.secrets["claude"]["api_key"]

# Funzione per generare un articolo con Claude 3.5 Sonnet
def generate_article_claude():
    url = "https://api.anthropic.com/v1/messages"  # Endpoint corretto
    headers = {
        "anthropic-api-key": claude_api_key,  # Chiave API corretta
        "Content-Type": "application/json",
    }

    # Prompt per generare l'articolo
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

    # Dati della richiesta
    payload = {
        "model": "claude-3-5-sonnet-20241022",  # Specifica il modello
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens_to_sample": 4096,  # Imposta il limite di token
        "temperature": 0.7,  # Controlla la creatività
    }

    try:
        # Invio della richiesta
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            # Parsing della risposta
            response_json = response.json()
            completion = response_json.get("completion", "").strip()
            return completion  # Restituisce il contenuto generato
        else:
            # Gestione degli errori
            st.error(f"Errore nella risposta di Claude: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per pubblicare l'articolo su WordPress
def publish_to_wordpress(title, content, image_url=None):
    wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]

    post_data = {
        'title': title,
        'content': content,
        'status': 'publish',
    }

    if image_url:
        post_data['featured_media'] = image_url  # Usa l'URL dell'immagine come copertura

    try:
        response = requests.post(wp_url, json=post_data, auth=(wp_user, wp_password))

        if response.status_code == 201:
            st.success(f"Articolo '{title}' pubblicato con successo!")
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore nella pubblicazione su WordPress: {e}")

# Streamlit UI per la generazione e pubblicazione dell'articolo
def main():
    st.title("Generatore di Articoli con Claude 3.5 Sonnet")

    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")
        # Genera il contenuto tramite Claude AI
        guide_content = generate_article_claude()

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Pulsante per pubblicare l'articolo
            if st.button("Pubblica Articolo"):
                title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
                publish_to_wordpress(title, guide_content)
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


