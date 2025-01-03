import streamlit as st
import requests

# Funzione per generare l'articolo con DeepSeek V3
def generate_article_deepseek():
    prompt = (
        "Scrivi una guida di almeno 1000 parole come se fossi uno psicologo con questo stile: "
        "Un tono leggero ma professionale, l'uso di ironia e humor, esempi concreti mescolati con battute, "
        "un approccio anticonvenzionale ma informato, la prospettiva in prima persona, metafore divertenti ma pertinenti, "
        "empatia e calore umano. Usa paragrafi chiari, titoli e sottotitoli (con grassetti, sottolineature, caratteri di dimensione maggiore) "
        "per organizzare il contenuto, senza includere simboli inutili. "
        "Basa la scelta dell'argomento in base agli ultimi articoli di queste fonti affidabili: "
        "Psychology Today (sezione Latest), Science Daily (sezione Mind & Brain), American Psychological Association (sezione News), Nature Human Behaviour. "
        "Alla fine scrivi un disclaimer in cui spieghi che la guida non ha nessuna finalità nel fornire consigli psicologici o scientifici e che devono rivolgersi sempre a professionisti. "
        "Il titolo dovrai pensarlo sulla base dei contenuti generati e dovrà essere accattivante. "
        "Inizialmente non devi scrivere ecco a te il contenuto. Parti subito con la guida."
    )
    
    # Endpoint e chiave API di DeepSeek
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['deepseek']['api_key']}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",  # Modello DeepSeek V3
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False  # Impostato su False per una risposta non in streaming
    }

    try:
        # Richiesta POST per generare l'articolo
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            # Estrarre il contenuto generato
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            return content.strip()
        else:
            st.error(f"Errore nella risposta DeepSeek: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Errore durante la generazione dell'articolo: {e}")
        return None

# Funzione principale per Streamlit
def main():
    st.title("Generatore di Articoli con DeepSeek V3")

    # Pulsante per generare l'articolo
    if st.button("Genera Articolo"):
        st.write("Generazione della guida in corso...")
        guide_content = generate_article_deepseek()

        if guide_content:
            # Mostra il contenuto generato
            st.subheader("Contenuto Generato:")
            st.write(guide_content)
        else:
            st.error("Non è stato possibile generare l'articolo.")

# Avvia l'app Streamlit
if __name__ == "__main__":
    main()


