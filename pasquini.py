import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# Funzione per generare l'articolo con DeepSeek
def generate_article_deepseek(prompt):
    try:
        # Chiamata all'API di DeepSeek
        payload = {
            "model": "deepseek-chat",  # Modello DeepSeek V3
            "prompt": prompt,  # Usa il campo prompt per passare l'argomento
        }

        # Debugging: Stampa del corpo della richiesta per verificare la struttura
        st.write("Payload della richiesta:", payload)

        response = requests.post(
            "https://api.deepseek.com/beta/v1/completions",  # Endpoint per completions di DeepSeek
            headers={
                "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",  # API Key DeepSeek
                "Content-Type": "application/json",
            },
            json=payload,
        )

        # Debugging: Stampa lo status code e il contenuto della risposta
        st.write("Status Code:", response.status_code)
        st.write("Response Text:", response.text)

        if response.status_code == 200:
            response_json = response.json()
            # Estrae il testo dalla risposta corretta
            content = response_json.get("choices", [])[0].get("text", "").strip()  # Cambiato 'message' in 'text'
            return content  # Restituisce il testo dell'articolo
        else:
            st.error(f"Errore nella risposta di DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per pubblicare come bozza su WordPress
def publish_to_wordpress(title, content):
    wp_url = "https://www.psicoo.it/wp-json/wp/v2/posts"  # Endpoint WordPress
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    post_data = {
        'title': title,
        'content': content,
        'status': 'draft',  # Lo status è impostato su 'draft' per salvarlo come bozza
    }

    try:
        response = requests.post(wp_url, json=post_data, auth=wp_auth)
        st.write("Risposta dall'API WordPress:", response.status_code, response.text)  # Log della risposta

        if response.status_code == 201:
            st.success("Articolo salvato come bozza su WordPress!")
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Streamlit UI per la generazione e pubblicazione dell'articolo
def main():
    st.title("Generatore di Articoli con DeepSeek")

    # Casella di testo per l'inserimento opzionale di tematiche
    tema = st.text_input("Inserisci le tematiche di interesse (opzionale)", "")

    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")

        # Definisci il prompt esatto
        prompt = (
            "Scrivi una guida di almeno 1000 parole come se fossi uno psicologo con questo stile: "
            "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
            "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
            "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di dimensione maggiore) "
            "per organizzare il contenuto, senza includere simboli inutili. "
            "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
            "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), "
            "Nature Human Behaviour. "
            "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici "
            "e che devono rivolgersi sempre a professionisti. "
            "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante. "
            "Inizialmente non devi scrivere ecco a te il contenuto. Parti subito con la guida."
        )

        # Se l'utente inserisce una tematica, la includiamo nel prompt
        if tema:
            prompt += f" Le tematiche di interesse sono: {tema}."

        # Genera il contenuto tramite DeepSeek
        guide_content = generate_article_deepseek(prompt)

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Salva automaticamente come bozza su WordPress
            title = guide_content.split('\n')[0]  # Usa la prima riga come titolo
            publish_to_wordpress(title, guide_content)  # Salva come bozza
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


