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
def generate_article_claude(keywords):
    prompt = f"Genera un articolo ben scritto e informativo basato sulle parole chiave: {keywords}. L'articolo deve essere leggibile, ottimizzato per SEO, e privo di simboli superflui come asterischi, segni, hashtag o markdown. Usa paragrafi chiari, titoli e sottotitoli per organizzare il contenuto, senza includere simboli inutili."

    try:
        # Creazione di un batch di richieste con Claude
        message_batch = client.beta.messages.batches.create(
            requests=[
                {
                    "custom_id": "article-prompt",
                    "params": {
                        "model": "claude-3-5-haiku-20241022",  # Modello di Claude, modificabile
                        "max_tokens": 1000,
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
    # Aggiungi formattazione per i titoli (ad esempio, righe che cominciano con "Titolo" o "Sezione")
    content = content.replace("\nTitolo", "<h2>").replace("Titolo", "</h2>")
    content = content.replace("\nSezione", "<h3>").replace("Sezione", "</h3>")

    # Esegui una serie di sostituzioni per aggiungere la formattazione
    content = content.replace("*", "<b>").replace("*", "</b>")  # Sostituire *con <b> per grassetto
    content = content.replace("_", "<i>").replace("_", "</i>")  # Sostituire _ con <i> per corsivo
    content = content.replace("~", "<u>").replace("~", "</u>")  # Sostituire ~ con <u> per sottolineato

    # Aggiungi uno spazio tra le righe per i paragrafi
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
st.title("Generatore di articoli con Claude AI")
keywords = st.text_input("Inserisci le parole chiave")

if st.button("Genera e Pubblica Articolo"):
    if keywords.strip():  # Verifica che le parole chiave non siano vuote
        st.info("Generazione dell'articolo in corso...")
        article_content = generate_article_claude(keywords)
        st.write("Contenuto generato:", article_content)  # Debug
        if article_content:
            # Formattiamo il contenuto prima di inviarlo
            formatted_content = format_content(article_content)
            title = keywords.capitalize()  # Usa le parole chiave come titolo, ma personalizzato se necessario
            title = title.replace("Articolo su", "").strip()  # Rimuove "Articolo su" se presente
            publish_to_wordpress(title, formatted_content)
    else:
        st.warning("Inserisci delle parole chiave valide!")

