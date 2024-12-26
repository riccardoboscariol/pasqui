import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import json

# Configurazione di Claude
# Inserisci qui il tuo API key di Claude
claude_api_key = "YOUR_CLAUDE_API_KEY"

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
        response = requests.post(
            "https://api.claude.ai/messages",
            headers={"Authorization": f"Bearer {claude_api_key}"},
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "system": "You are a helpful and creative assistant.",
                "messages": [{"role": "user", "content": prompt}],
            },
        )

        if response.status_code == 200:
            response_json = response.json()

            # Estrai il testo dal campo TextBlock
            if 'content' in response_json['message']:
                text_content = ''.join([block['text'] for block in response_json['message']['content']])
                return text_content.strip()  # Restituisci il contenuto concatenato
            else:
                st.error("La risposta non contiene il campo 'content'. Risposta completa: " + str(response_json))
                return ""
        else:
            st.error(f"Errore nella risposta di Claude: {response.status_code} - {response.text}")
            return ""
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per pubblicare l'articolo su WordPress
def publish_to_wordpress(title, content):
    # Configurazione dell'API di WordPress
    wp_url = "https://your-wordpress-site.com/wp-json/wp/v2/posts"
    wp_user = "your_username"
    wp_password = "your_password"
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    # Prepara i dati per la richiesta
    post_data = {
        'title': title,
        'content': content,
        'status': 'publish'  # Può essere 'draft' o 'publish'
    }

    try:
        # Fai la richiesta POST per creare un nuovo articolo su WordPress
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

            # Pulsante per pubblicare l'articolo
            if st.button("Pubblica Articolo"):
                # Estrai il titolo dal contenuto generato (puoi personalizzare questa logica)
                title = "Guida Psicologica: Come Gestire la Sindrome dell'Impostore"
                publish_to_wordpress(title, guide_content)

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()




