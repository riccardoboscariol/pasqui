import streamlit as st
import google.generativeai as palm
from anthropic import Client as ClaudeClient
from wordpress_xmlrpc import Client as WPClient, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost

# Configura le chiavi API
GEMINI_API_KEY = st.secrets["gemini"]["api_key"]
CLAUDE_API_KEY = st.secrets["claude"]["api_key"]
WORDPRESS_URL = st.secrets["wordpress"]["url"]
WORDPRESS_USER = st.secrets["wordpress"]["username"]
WORDPRESS_PASSWORD = st.secrets["wordpress"]["password"]

# Configura Gemini e Claude
palm.configure(api_key=GEMINI_API_KEY)
claude_client = ClaudeClient(api_key=CLAUDE_API_KEY)

# Funzione per generare l'articolo con Gemini
def generate_article_gemini():
    try:
        response = palm.generate_text(
            model="text-bison-001",
            prompt=(
                "Scrivi una guida di almeno 1000 parole su un argomento psicologico generico. "
                "Il tono deve essere leggero ma professionale, con ironia, humor e esempi pratici. "
                "Struttura il contenuto in paragrafi chiari con titoli e sottotitoli."
            ),
            temperature=0.7,
            max_output_tokens=2000,
        )
        return response.get('text', '')
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo con Gemini: {e}")
        return ""

# Funzione per migliorare l'articolo con Claude
def refine_article_with_claude(content):
    prompt = (
        "\n\nHuman: Migliora il seguente articolo, adattandolo al tono richiesto: "
        "un tono leggero ma professionale, con ironia, humor, esempi pratici e uno stile accattivante. "
        "Organizza i paragrafi, aggiungi titoli pertinenti e assicurati che l'articolo sia chiaro e scorrevole. "
        "Non modificare il contenuto in modo sostanziale, ma rendilo più fluido e interessante.\n\n"
        f"Articolo:\n{content}\n\nAssistant:"
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
        st.error(f"Errore durante la modifica dell'articolo con Claude: {e}")
        return ""

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
st.title("Generatore di articoli con Gemini e Claude")

if st.button("Genera e Pubblica Articolo"):
    st.info("Generazione dell'articolo con Gemini in corso...")
    gemini_content = generate_article_gemini()
    if gemini_content:
        st.success("Articolo generato con successo da Gemini!")
        st.write("Articolo grezzo generato:", gemini_content)

        st.info("Adattamento dell'articolo con Claude in corso...")
        refined_content = refine_article_with_claude(gemini_content)
        if refined_content:
            st.success("Articolo migliorato con successo da Claude!")
            st.write("Articolo finale:", refined_content)

            st.info("Pubblicazione dell'articolo su WordPress in corso...")
            title = "Guida Psicologica Generata"
            publish_to_wordpress(title, refined_content)


