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
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di differente grandezza, per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili dove cercare articoli recenti di psicologia: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour."
        "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici e che devono rivolgersi sempre a professionisti"
        "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante."
        "Inizialmente non devi scrivere ecco a te il contenuto. Parti subito con la guida."
        "Per capire bene lo stile e cosa vorrei ecco a te una guida scritta. La tua non dovrà essere uguale ma simile nella cifra stilistica addottata. Testo: Premessa Necessaria Cari amici dal cuore ferito (o confuso, o tentato), parliamo di quel fenomeno che nessuno vuole affrontare ma che, secondo gli studi, interessa circa il 25-40% delle relazioni. L’infedeltà è come un terremoto emotivo: può radere al suolo tutto o può spingere a ricostruire qualcosa di più solido. Dipende da come si gestisce la scossa. 1. Cosa Dice la Scienza (Perché fa Sempre Figo Citare gli Studi) I Numeri che Non Volevate Sapere Il 20-25% delle coppie sposate sperimenta infedeltà fisica Il 40% ammette infedeltà emotiva (sì, flirtare su Instagram conta) Il 65% delle relazioni sopravvive al tradimento (con terapia e molto gelato) L’85% dei tradimenti avviene con persone che si consideravano “solo amici” (sì, proprio quel collega “simpatico”) Tipi di Infedeltà (Perché Non è Tutto Bianco o Nero) Fisica: Il classico intramazzo di lenzuola Emotiva: Quando il cuore fa il pendolare Digitale: Dal sexting ai like compulsivi su Instagram Micro-tradimenti: Quelle piccole azioni al confine tra amicizia e flirt 2. Quando Succede a Te: La Guida del Sopravvissuto Se Sei Stato Tradito (E Vorresti Dare Fuoco al Mondo) Fase 1: Il Trauma Iniziale ecc."
    )

    try:
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
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
        title = "Guida psicologica basata su fonti affidabili"
        publish_to_wordpress(title, formatted_content)




