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
        "Scrivi una guida di almeno 1000 parole come se fossi uno psicologo con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Usa paragrafi chiari, **titoli e sottotitoli in grassetto e con caratteri più grandi** "
        "per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), APA (sezione News), Nature Human Behaviour. "
        "Alla fine, aggiungi un disclaimer che spieghi che la guida non fornisce consigli psicologici specifici. "
        "Inizia direttamente con la guida senza alcuna introduzione o frase superflua."
    )

    try:
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['completion']
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per estrarre il titolo dall'articolo
def extract_title_from_content(content):
    # Estrarre la prima frase o il primo titolo come titolo dell'articolo
    title_end = content.find("\n")  # Fine del primo paragrafo o titolo
    title = content[:title_end].strip()
    return title if len(title) > 5 else "Articolo Psicologico Accattivante"

# Funzione per applicare la formattazione HTML
def format_content(content):
    # Aggiungi formattazione per WordPress
    formatted_content = content.replace("\n\n", "</p><p>").replace("\n", "<br>")
    formatted_content = formatted_content.replace("**", "<strong>")  # Grassetto
    formatted_content = formatted_content.replace("# ", "<h1>").replace("## ", "<h2>")  # Titoli
    return f"<p>{formatted_content}</p>"

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
    if guide_content:
        st.success("Articolo generato con successo!")
        st.write("Anteprima contenuto generato:", guide_content)

        # Estrazione del titolo
        title = extract_title_from_content(guide_content)
        st.write("Titolo estratto:", title)

        # Formattazione del contenuto
        formatted_content = format_content(guide_content)
        
        # Pubblicazione su WordPress
        st.info("Pubblicazione su WordPress in corso...")
        publish_to_wordpress(title, formatted_content)




