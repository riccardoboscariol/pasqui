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

        response = requests.post(
            "https://api.deepseek.com/beta/v1/completions",  # Endpoint per completions di DeepSeek
            headers={
                "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",  # API Key DeepSeek
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if response.status_code == 200:
            response_json = response.json()
            content = response_json.get("choices", [])[0].get("text", "").strip()
            return content
        else:
            st.error(f"Errore nella risposta di DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione per formattare il testo in HTML (con titoli, grassetto, ecc.)
def format_content_for_html(content):
    content = content.strip()

    # Formattiamo i titoli: sostituisce "# " con tag HTML per i titoli
    content = content.replace("# ", "<h2><b>").replace("\n", "</b></h2>\n")

    # Rimuoviamo eventuali "#" isolati alla fine dei paragrafi
    lines = content.split("\n")
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("#"):  # Se una linea inizia con "#", è un titolo
            cleaned_lines.append(line)  # Manteniamo intatta
        else:
            cleaned_lines.append(line.rstrip("#"))  # Rimuoviamo i "#" solo alla fine

    content = "\n".join(cleaned_lines)

    # Rimuoviamo le linee "---"
    content = content.replace("---", "")

    # Rimuoviamo i simboli "##"
    content = content.replace("##", "")

    # Rimuoviamo il simbolo "*" per il grassetto
    content = content.replace("**", "")

    # Aggiungiamo paragrafi
    content = content.replace("\n", "<p>").replace("</p>\n", "</p>\n")

    return content

# Funzione per pubblicare come bozza su WordPress
def publish_to_wordpress(title, content):
    wp_url = "https://www.psicoo.it/wp-json/wp/v2/posts"  # Endpoint WordPress
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    formatted_content = format_content_for_html(content)

    post_data = {
        'title': title,
        'content': formatted_content,
        'status': 'draft',  # Salva come bozza
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
            "Scrivi una guida lunga almeno 3000 parole come se fossi uno psicologo con questo stile: "
            "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
            "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
            "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di dimensione maggiore) "
            "per organizzare il contenuto, senza includere simboli inutili. "
            "Vedi di non essere troppo semplicistico, comico o poco serio, bilancia ironia a informazione e professionalità."
            "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
            "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), "
            "Nature Human Behaviour. "
            "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici "
            "e che devono rivolgersi sempre a professionisti. "
            "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante. "
            "Fai delle citazioni quando puoi, di studi, ricerche o libri e riportale in una bibliografia accurata e verificata alla fine dell'articolo."
            "Cerca anche se ci sono libri in italiano e citali in bibliografia. Controlla che siano esistenti su Amazon prima di citarli."
        )

        if tema:
            prompt += f" Le tematiche di interesse sono: {tema}."

        guide_content = generate_article_deepseek(prompt)

        if guide_content:
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Estrai titolo e contenuto:
            title_line = guide_content.split('\n')[0].strip().replace('"', '')  # Prima linea come titolo
            title = title_line if title_line else "Titolo Mancante"

            # Se la seconda linea è il sottotitolo, usala solo come contenuto
            guide_content = "\n".join(guide_content.split('\n')[1:])

            publish_to_wordpress(title, guide_content)  # Salva come bozza
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()



