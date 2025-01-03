import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# Funzione per generare l'articolo con DeepSeek V3
def generate_article_deepseek(theme=None):
    # Prompt base
    base_prompt = (
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

    # Aggiungi la tematica al prompt, se specificata
    if theme:
        base_prompt += f" Concentrati sull'area tematica seguente: {theme}."

    # Configura la richiesta a DeepSeek
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",  # Modello DeepSeek V3
        "messages": [
            {"role": "user", "content": base_prompt}
        ],
        "stream": False  # Risposta completa, non streaming
    }

    try:
        # Richiesta POST per generare l'articolo
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            return content.strip()
        else:
            st.error(f"Errore nella risposta DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per pubblicare l'articolo su WordPress come bozza
def publish_to_wordpress(title, content, image_url=None):
    wp_url = st.secrets["wordpress"]["url"].replace("xmlrpc.php", "wp-json/wp/v2/posts")
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    # Prepara i dati del post
    post_data = {
        'title': title,
        'content': content,
        'status': 'draft',  # Salvato come bozza
    }

    if image_url:
        post_data['featured_media'] = image_url  # Aggiungi immagine, se presente

    try:
        response = requests.post(wp_url, json=post_data, auth=wp_auth)

        # Debug per visualizzare i dettagli della richiesta
        st.write("Dati inviati a WordPress:", post_data)
        st.write("Stato della risposta:", response.status_code)
        st.write("Risposta completa:", response.text)

        if response.status_code == 201:
            st.success(f"Articolo '{title}' salvato come bozza su WordPress!")
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Funzione principale per Streamlit
def main():
    st.title("Generatore di Articoli con DeepSeek V3")
    
    # Casella di testo per indicare un'area tematica opzionale
    theme = st.text_input("Indica una tematica (opzionale)", value="")
    
    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")
        guide_content = generate_article_deepseek(theme.strip() if theme else None)

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Pulsante per salvare come bozza su WordPress
            if st.button("Salva come bozza su WordPress"):
                title = guide_content.split('\n')[0]  # Usa la prima riga del contenuto come titolo
                publish_to_wordpress(title, guide_content)
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()

