import streamlit as st
from anthropic import Client as ClaudeClient
from google.generativeai import palm
from wordpress_xmlrpc import Client as WPClient, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# Recupera le informazioni dalle secrets di Streamlit
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Configura le API di Claude e Gemini
claude_client = ClaudeClient(api_key=CLAUDE_API_KEY)
palm.configure(api_key=GEMINI_API_KEY)

# Funzione per generare l'articolo con Gemini
def generate_article_gemini():
    prompt = (
        "Scrivi una guida di almeno 1000 parole con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli per organizzare il contenuto, senza includere simboli inutili. "
        "L'articolo deve trattare un argomento psicologico generico in modo informativo, senza fornire consigli clinici diretti. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili dove cercare articoli recenti di psicologia: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour."
    )

    try:
        # Richiesta a Gemini per generare il contenuto
        response = palm.generate_text(
            prompt=prompt,
            model="models/text-bison-001",  # Usa il modello corretto di Gemini
            temperature=0.7,
            max_output_tokens=3000
        )

        if "text" in response:
            return response["text"]
        else:
            st.error("Errore: La risposta di Gemini non contiene il testo previsto.")
            return ""
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo con Gemini: {e}")
        return ""

# Funzione per perfezionare il testo con Claude
def refine_with_claude(content):
    prompt = (
        f"Prendi il seguente articolo e sistemalo con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Assicurati che sia ben organizzato con titoli e sottotitoli chiari, e formattato correttamente."
        "\n\nArticolo originale:\n\n"
        f"{content}"
        "\n\nAssistant:"
    )

    try:
        response = claude_client.completions.create(
            model="claude-2",
            prompt=prompt,
            max_tokens_to_sample=2000,
        )

        if hasattr(response, 'completion'):
            return response.completion
        else:
            st.error("Errore: La risposta di Claude non contiene il testo previsto.")
            return ""
    except Exception as e:
        st.error(f"Errore durante la rifinitura dell'articolo con Claude: {e}")
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
st.title("Generatore di guide con Gemini e Claude AI")

if st.button("Genera e Pubblica Guida"):
    st.info("Generazione dell'articolo in corso con Gemini...")
    gemini_content = generate_article_gemini()
    st.write("Articolo generato da Gemini (grezzo):", gemini_content)  # Debug

    if gemini_content:
        st.info("Rifinitura dell'articolo in corso con Claude...")
        refined_content = refine_with_claude(gemini_content)
        st.write("Articolo perfezionato da Claude:", refined_content)  # Debug

        if refined_content:
            formatted_content = format_content(refined_content)
            title = "Guida psicologica basata su fonti affidabili"
            publish_to_wordpress(title, formatted_content)

