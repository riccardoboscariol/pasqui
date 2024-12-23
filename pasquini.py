import streamlit as st
import anthropic
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# Recupera le informazioni dalle secrets di Streamlit
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Inizializza il client di Claude
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Funzione per generare l'articolo con Claude AI
def generate_article_claude():
    prompt = (
        "Scrivi una guida di almeno 3000 parole come se fossi uno psicologo con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili dove cercare articoli recenti di psicologia: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour."
    )

    try:
        # Creazione di un batch di richieste con Claude
        message_batch = client.beta.messages.batches.create(
            requests=[
                {
                    "custom_id": "guide-prompt",
                    "params": {
                        "model": "claude-3-5-haiku-20241022",  # Modello di Claude, modificabile
                        "max_tokens": 3000,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt,
                            }
                        ],
                    },
                }
            ]
        )

        # Estrai il contenuto dalla risposta
        response = message_batch['results'][0]['response']['text']
        return response

    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per applicare la formattazione HTML
def format_content(content):
    # Esegui una serie di sostituzioni per aggiungere la formattazione
    content = content.replace("\nTitolo", "<h2>").replace("Titolo", "</h2>")
    content = content.replace("\nSezione", "<h3>").replace("Sezione", "</h3>")
    content = content.replace("*", "<b>").replace("*", "</b>")
    content = content.replace("_", "<i>").replace("_", "</i>")
    content = content.replace("~", "<u>").replace("~", "</u>")
    content = content.replace("\n", "<br>")  # Aggiunge <br> per i ritorni a capo

    return content

# Funzione per pubblicare su WordPress
def publish_to_wordpress(title, content):
    if not content.strip():
        st.error("Errore: Il contenuto dell'articolo è vuoto. Verifica la generazione dell'articolo.")
        return

    try:
        # Crea la connessione al sito WordPress
        wp = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)

        # Crea un nuovo post WordPress
        post = WordPressPost()
        post.title = title
        post.content = content  # Il contenuto che contiene già HTML
        post.post_status = "publish"  # Pubblica l'articolo immediatamente

        # Invia il post tramite la API XML-RPC
        wp.call(NewPost(post))
        st.success("Articolo pubblicato con successo!")
    except Exception as e:
        st.error(f"Errore durante la pubblicazione su WordPress: {e}")

# Streamlit UI
st.title("Generatore di guide con Claude AI")

if st.button("Genera e Pubblica Guida"):
    st.info("Generazione della guida in corso...")
    guide_content = generate_article_claude()
    st.write("Contenuto generato:", guide_content)  # Debug
    if guide_content:
        # Formattiamo il contenuto prima di inviarlo
        formatted_content = format_content(guide_content)
        title = "Guida psicologica basata su fonti affidabili"  # Titolo generico per l'articolo
        publish_to_wordpress(title, formatted_content)


