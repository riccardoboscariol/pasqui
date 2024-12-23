import streamlit as st
from anthropic import Client
from wordpress_xmlrpc import Client as WPClient, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# Recupera le informazioni dalle secrets di Streamlit
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Inizializza il client di Claude
claude_client = Client(api_key=CLAUDE_API_KEY)

# Funzione per generare l'articolo con Claude AI
def generate_article_claude():
    prompt = (
        "\n\nHuman: Scrivi una guida di circa 500 parole per aiutare le persone a gestire lo stress in modo sano e costruttivo. "
        "Dovresti includere tecniche di rilassamento, approcci psicologici utili e pratici suggerimenti da applicare nella vita quotidiana. "
        "Il tono dovrebbe essere professionale ma accessibile, con alcuni esempi pratici di come queste tecniche possono essere messe in pratica, "
        "senza includere simboli inutili e seguendo le linee guida etiche."
        "\n\nAssistant:"
    )

    try:
        # Creazione di una richiesta a Claude con il metodo corretto
        response = claude_client.completions.create(
            model="claude-2",  # Modello corretto
            prompt=prompt,     # Il prompt che fornisci per generare l'articolo
            max_tokens_to_sample=1000,    # Numero massimo di token da generare
        )

        # Debug: Stampa l'intera risposta per capire la sua struttura
        st.write("Risposta completa di Claude:", response)

        # Estrai il completamento dalla risposta
        if hasattr(response, 'completion'):  # Verifica se 'response' ha l'attributo 'completion'
            return response.completion
        else:
            st.error("Errore: La risposta di Claude non contiene il testo previsto.")
            return ""

    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per applicare la formattazione HTML
def format_content(content):
    content = content.replace("\n", "<br>")
    return content

# Funzione per pubblicare su WordPress
def publish_to_wordpress(title, content):
    if not content.strip():
        st.error("Errore: Il contenuto dell'articolo è vuoto. Verifica la generazione dell'articolo.")
        return

    try:
        wp = WPClient(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)
        post = WordPressPost()
        post.title = title
        post.content = content
        post.post_status = "publish"
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
        formatted_content = format_content(guide_content)
        title = "Guida alla gestione dello stress"
        publish_to_wordpress(title, formatted_content)


