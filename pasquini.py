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
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di differente grandezza) "
        "per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour. "
        "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici e che devono rivolgersi sempre a professionisti. "
        "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante. "
        "Inizialmente non devi scrivere ecco a te il contenuto. Parti subito con la guida."
    )

    try:
        response = claude_client.completions.create(
            model="claude-2",
            messages=[{"role": "user", "content": prompt}],
            max_tokens_to_sample=3000
        )
        return response["completion"].strip()
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return ""

# Funzione per generare un titolo creativo basato sul contenuto
def extract_title_from_content(content):
    """
    Genera un titolo accattivante basato sul contenuto dell'articolo.
    Analizza le prime righe per creare un titolo che rifletta il tono creativo e il tema.
    """
    # Analizza le prime 200 parole per trovare un'idea di titolo
    first_paragraph = content[:200]  # Prende le prime 200 parole o meno
    
    # Prompt per generare il titolo creativo con Claude
    title_prompt = (
        f"Dal seguente contenuto genera un titolo creativo e accattivante. "
        f"Il titolo deve essere nello stile di questi esempi: "
        f"'La Mente Come Cinema: Guida (Decisamente Non Ossessiva) alla Gestione dei Pensieri Ripetitivi', "
        f"'L’Ansia Come Compagna di Viaggio: Manuale di Convivenza con la Tua Coinquilina Più Invadente', "
        f"'La (Semi)Scientifica Arte di Trovare l’Anima Gemella'. "
        f"Usa lo stesso tono per creare un titolo originale. "
        f"Ecco il contenuto da cui partire: {first_paragraph}"
    )

    try:
        response = claude_client.completions.create(
            model="claude-2",
            prompt=title_prompt,
            max_tokens_to_sample=50
        )
        title = response["completion"].strip()

        # Controllo che il titolo sia valido
        if len(title) > 10:
            return title
        else:
            return "Guida Psicologica Originale"
    except Exception as e:
        st.error(f"Errore durante la generazione del titolo: {e}")
        return "Guida Psicologica Originale"

# Funzione per applicare la formattazione HTML
def format_content(content):
    """
    Applica la formattazione HTML al contenuto per includere titoli in grassetto e paragrafi ben separati.
    """
    content = content.replace("\n", "<br>")
    return content

# Funzione per pubblicare su WordPress
def publish_to_wordpress(title, content):
    """
    Pubblica l'articolo generato su WordPress con il titolo e il contenuto forniti.
    """
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
st.title("Generatore di Guide Psicologiche")

if st.button("Genera e Pubblica Guida"):
    st.info("Generazione della guida in corso...")
    guide_content = generate_article_claude()
    st.write("Contenuto generato:", guide_content)  # Debug

    if guide_content:
        # Genera un titolo accattivante
        title = extract_title_from_content(guide_content)
        st.write("Titolo generato:", title)  # Debug

        # Formatta il contenuto in HTML
        formatted_content = format_content(guide_content)

        # Pubblica su WordPress
        publish_to_wordpress(title, formatted_content)

