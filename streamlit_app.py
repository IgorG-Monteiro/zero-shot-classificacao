import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_tags import st_tags

st.set_page_config(
    layout="centered", page_title="Modelo Zero-Shot",
    page_icon="😎"
)

c1, c2 = st.columns([0.32, 2])

with c1:

    st.image(
        "images/alvo.png",
        width=85,
    )

with c2:

    st.caption("")
    st.title("Classificador de texto Zero-Shot")


if not "valid_inputs_received" in st.session_state:
    st.session_state["valid_inputs_received"] = False

st.sidebar.write("")


with c1: st.sidebar.image(
    "images/huggingface-2.svg",
    width=50,
)

predefined_key = "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"

API_KEY = st.sidebar.text_input(
    "Coloque sua API do HuggingFace",
    help="Para conseguir a chave da sua API, primeiro crie uma conta gratuita no HuggingFace, após isso vá em 'https://huggingface.co/settings/tokens' e crie seu token.",
    type="password",
    value=predefined_key,
    )
    
API_URL = "https://api-inference.huggingface.co/models/valhalla/distilbart-mnli-12-3"

headers = {"Authorization": f"Bearer {API_KEY}"}

st.sidebar.markdown("---")

st.sidebar.write(
    "App criado por Igor a partir de um tutorial de streamlit e modelos Zero-Shot, utilizando modelo do HuggingFace: distilbart-mnli-12-3"
)

MainTab, InfoTab = st.tabs(["Main", "Info"])

with InfoTab: 

    st.image(
        "images/joke.jpg"
    )


with MainTab:

    st.write("")
    st.markdown(
        "Classifique frases com esse app. Não necessita de treinamento!"
    )
    st.write("")


    with st.form(key="my_form"):


        labels_from_st_tags = st_tags(
            value=["Clima", "Pergunta", "Afirmação"],
            maxtags=3,
            suggestions=["Clima", "Pergunta", "Afirmação"],
            label="",
        )

        MAX_KEY_PHRASES = 50

        new_line = "\n"

        pre_defined_keyphrases = [
            "Eu sou muito bom nisso!",
            "Quanto custa esse sorvete?",
            "O ar condicionado está muito frio.",
        ]

        keyphrases_string = f"{new_line.join(map(str, pre_defined_keyphrases))}"

        text = st.text_area(
            "Coloque frases para classificar",

            keyphrases_string,

            height=200,

            key="1",
        )


        text = text.split("\n")

        LinesList = []
        for x in text:
            LinesList.append(x)
        LinesList = list(dict.fromkeys(LinesList))

        LinesList = list(filter(None, LinesList))

        if len(LinesList) > MAX_KEY_PHRASES:
            st.info(
                f"Sua frase deve ter menos que 50 caracteres"
            )

            LinesList = LinesList[:MAX_KEY_PHRASES]

        submit_button = st.form_submit_button(label="Enviar")



# casos de teste

if not submit_button and not st.session_state.valid_inputs_received:
    st.stop()

elif submit_button and not text:
    st.warning("* Não tem Frase para classificar.")
    st.session_state.valid_inputs_received = False
    st.stop()

elif submit_button and not labels_from_st_tags:
    st.warning("* Você não adicinou 'labels', por favor adicione alguma.")
    st.session_state.valid_inputs_received = False
    st.stop()

elif submit_button and len(labels_from_st_tags) == 1:
    st.warning("* Por favor adicione ao menos 2 labels para a classificação")
    st.session_state.valid_inputs_received = False
    st.stop()

elif submit_button or st.session_state.valid_inputs_received:

    if submit_button:

        st.session_state.valid_inputs_received = True


# THE API CALL

def query(payload):
    response = requests.post(API_URL, headers=headers,
    json=payload)
    return response.json()


list_for_api_output = []



for row in LinesList:
    api_json_output = query(
        {
            "inputs": row,
            "parameters": {"candidate_labels":
                           labels_from_st_tags},
            "options": {"wait_for_model": True},
        }
    )


    list_for_api_output.append(api_json_output)

    df = pd.DataFrame.from_dict(list_for_api_output)




st.success("Prontinho! 👌")

st.caption("")
st.markdown("### Cheque os resultados!")
st.caption("")


def plot_bar(categories, scores, sentence):
    df_plot = pd.DataFrame({'labels': categories, 'scores': scores, 'sequence': sentence})
    fig = px.bar(df_plot, 
                 x='scores', 
                 y='labels', 
                 orientation='h', 
                 text='scores', 
                 title=sentence,
                 color='scores',
                 color_continuous_scale='purples')
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside', width=0.2)
    fig.update_layout(
        xaxis_title='Pontuação',
        yaxis_title='Categorias',
        yaxis=dict(tickmode='linear'),
        template='simple_white',
        bargap=0
    )
    return fig

for i in range(len(df)):
    fig = plot_bar(df['labels'][i], df['scores'][i], df['sequence'][i])
    st.plotly_chart(fig)

st.caption("")
st.markdown("DataFrame retornado:")
st.write(df)
