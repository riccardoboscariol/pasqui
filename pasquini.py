import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# Funzione per generare l'articolo con DeepSeek
def generate_article_deepseek(prompt):
    try:
        payload = {
            "model": "deepseek-chat",
            "prompt": prompt,
        }

        response = requests.post(
            "https://api.deepseek.com/beta/v1/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code == 200:
            response_json = response.json()
            content = response_json.get("choices", [])[0].get("text", "").strip()
            return filter_relevant_content(content)
        else:
            st.error(f"Errore nella risposta di DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per filtrare contenuti non pertinenti
def filter_relevant_content(content):
    lines = content.split("\n")
    filtered_lines = []

    for line in lines:
        if "come gestire" in line.lower():  # Esempio di filtro basato su parole chiave non pertinenti
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines)

# Funzione per formattare il testo in HTML (con titoli, grassetto, ecc.)
def format_content_for_html(content):
    content = content.strip()

    # Gestione dei simboli # nei titoli
    lines = content.split("\n")
    formatted_lines = []

    for line in lines:
        if line.startswith("# "):  # Titoli principali
            line = line.replace("# ", "<h2><b>").strip() + "</b></h2>"
        elif line.startswith("## "):  # Sottotitoli
            line = line.replace("## ", "<h3>").strip() + "</h3>"
        elif line.startswith("### "):  # Sotto-sottotitoli
            line = line.replace("### ", "<h4>").strip() + "</h4>"
        else:  # Paragrafi normali
            line = line.rstrip("#")  # Rimuove simboli # isolati alla fine
            line = f"<p>{line.strip()}</p>"

        formatted_lines.append(line)

    content = "\n".join(formatted_lines)
    return content

# Funzione per pubblicare come bozza su WordPress
def publish_to_wordpress(title, content):
    wp_url = "https://www.psicoo.it/wp-json/wp/v2/posts"
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    formatted_content = format_content_for_html(content)

    post_data = {
        'title': title,
        'content': formatted_content,
        'status': 'draft',
    }

    try:
        response = requests.post(wp_url, json=post_data, auth=wp_auth)
        if response.status_code == 201:
            st.success("Articolo salvato come bozza su WordPress!")
        else:
            st.error(f"Errore nella pubblicazione su WordPress: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Streamlit UI per la generazione e pubblicazione dell'articolo
def main():
    st.title("Generatore di Articoli con DeepSeek")

    tema = st.text_input("Inserisci le tematiche di interesse (opzionale)", "")

    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")

        prompt = (
            f"Scrivi una guida lunga almeno 3000 parole come se fossi uno psicologo esperto. "
            f"Focalizzati su questo argomento: {tema}. Includi consigli pratici, sottotitoli chiari e uno stile accessibile. "
            f"Evita elenchi infiniti e rimani concentrato sul tema."
        )

        content = generate_article_deepseek(prompt)

        if content:
            st.write(content)

            if st.button("Pubblica come bozza su WordPress"):
                publish_to_wordpress(tema, content)

if __name__ == "__main__":
    main()


