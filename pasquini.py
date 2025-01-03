import requests
import streamlit as st
from requests.auth import HTTPBasicAuth

# Funzione per formattare il contenuto in HTML (con titoli, grassetto, ecc.)
def format_content_for_html(content):
    # Rimuoviamo simboli non necessari dal titolo (es. "#") e virgolette
    content = content.strip()  # Rimuove eventuali spazi o simboli all'inizio e alla fine

    # Formattiamo i titoli
    content = content.replace("# ", "<h2><b>").replace("\n", "</b></h2>\n")  # Titolo grassetto e grande

    # Formattiamo il testo del corpo (senza grassetto)
    content = content.replace("**", "").replace("**", "")  # Rimuoviamo eventuale grassetto nel corpo del testo

    # Aggiungiamo paragrafi
    content = content.replace("\n", "<p>").replace("</p>\n", "</p>\n")  # Paragrafi

    return content

# Estrazione del titolo senza simboli
def extract_title(content):
    # Estrai il primo paragrafo come titolo e rimuovi simboli come #, virgolette e grassetto
    title_line = content.split('\n')[0].strip("#").strip().replace('"', '').replace('**', '')
    return title_line

# Funzione per pubblicare come bozza su WordPress
def publish_to_wordpress(title, content):
    wp_url = "https://www.psicoo.it/wp-json/wp/v2/posts"  # Endpoint WordPress
    wp_user = st.secrets["wordpress"]["username"]
    wp_password = st.secrets["wordpress"]["password"]
    wp_auth = HTTPBasicAuth(wp_user, wp_password)

    # Formattiamo il contenuto con HTML
    formatted_content = format_content_for_html(content)

    post_data = {
        'title': title,
        'content': formatted_content,  # Il contenuto formattato in HTML
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

# Funzione principale
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
            # Estrai il titolo senza simboli
            title = extract_title(guide_content)
            st.subheader("Contenuto Generato:")
            st.write(guide_content)

            # Pubblica il contenuto come bozza su WordPress
            publish_to_wordpress(title, guide_content)  # Salva come bozza
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


