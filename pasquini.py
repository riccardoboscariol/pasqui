import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# Funzione per generare l'articolo con DeepSeek
def generate_article_deepseek(prompt):
    try:
        # Chiamata all'API di DeepSeek con l'endpoint beta
        response = requests.post(
            "https://api.deepseek.com/beta/v1/completions",  # Endpoint beta per completions di DeepSeek
            headers={
                "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",  # API Key DeepSeek
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",  # Modello DeepSeek V3
                "prompt": prompt,  # Aggiungiamo il campo 'prompt'
                "max_tokens": 1500,  # Imposta un limite di token per la risposta
            },
        )

        # Debugging: Stampa lo status code e il contenuto della risposta
        st.write("Status Code:", response.status_code)
        st.write("Response Text:", response.text)

        if response.status_code == 200:
            response_json = response.json()
            content = response_json.get("choices", [])[0].get("text", "")  # Cambia 'message' con 'text'
            return content.strip()  # Restituisce il testo dell'articolo
        else:
            st.error(f"Errore nella risposta di DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per pubblicare o salvare come bozza su WordPress
def publish_to_wordpress(title, content, draft=False):
    wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    # Cambia lo stato del post in base al parametro draft
    post_data = {
        'title': title,
        'content': content,
        'status': 'draft' if draft else 'publish',
    }

    try:
        response = requests.post(wp_url, json=post_data, auth=wp_auth)
        st.write("Risposta dall'API WordPress:", response.status_code, response.text)  # Log della risposta

        if response.status_code == 201:
            return True  # Articolo salvato con successo
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
            return False  # Errore nel salvataggio
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")
        return False

# Streamlit UI per la generazione e pubblicazione dell'articolo
def main():
    st.title("Generatore di Articoli con DeepSeek")

    # Casella di testo per l'inserimento opzionale di tematiche
    tema = st.text_input("Inserisci le tematiche di interesse (opzionale)", "")

    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")

        # Modifica il prompt in base alla tematica inserita
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

        # Aggiungi la tematica se è presente
        if tema:
            prompt += f" Le tematiche di interesse sono: {tema}."

        # Genera il contenuto tramite DeepSeek
        guide_content = generate_article_deepseek(prompt)

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Pulsante per salvare come bozza su WordPress
            if st.button("Salva come Bozza"):
                title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
                success = publish_to_wordpress(title, guide_content, draft=True)  # Salva come bozza
                if success:
                    st.success("Articolo salvato come bozza su WordPress!")
                else:
                    st.error("Errore durante il salvataggio come bozza.")

            # Pulsante per pubblicare l'articolo su WordPress
            if st.button("Pubblica Articolo"):
                title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
                success = publish_to_wordpress(title, guide_content, draft=False)  # Pubblica l'articolo
                if success:
                    st.success(f"Articolo '{title}' pubblicato con successo!")
                else:
                    st.error(f"Errore durante la pubblicazione su WordPress.")
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


