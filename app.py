import streamlit as st
from PIL import Image
from io import BytesIO
import torch

from utils import load_pipeline, generate_image

torch.cuda.empty_cache()

base_models = {
    "Stable Diffusion 2": "stabilityai/stable-diffusion-2",
    "Stable Diffusion v1.4": "CompVis/stable-diffusion-v1-4",
}

style_models = {
    "Van Gogh Diffusion": "dallinmackay/Van-Gogh-diffusion",
    "Ghibli Diffusion": "nitrosocke/Ghibli-Diffusion",
    "disney-pixar-cartoon": "lavaman131/cartoonify",
   
}

samplers = ["LMS", "Euler", "DPM++"]

st.title("Geração de imagens com Stable Diffusion")

# Prompt e parâmetros
prompt = st.text_input("Prompt", "a photograph of an astronaut riding a horse")
negative_prompt = st.text_input("Negative Prompt", "blurry, low quality, distorted")

uploaded_image = st.file_uploader("Faça upload da imagem base (opcional)", type=["png", "jpg", "jpeg"])

# Escolha dos modelos
st.subheader("Modelo base")
use_base = st.checkbox("Usar modelo base", value=True)
base_model_choice = st.selectbox("Escolha o modelo base", list(base_models.keys()))
base_scheduler_choice = st.selectbox("Sampler", samplers, key="base_sampler")
base_strength = st.slider("Strength", 0.0, 1.0, 0.55, 0.05)
base_guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 6.0, 0.5)
base_steps = st.slider("Número de passos", 10, 100, 25, 1)


st.subheader("Modelo de Estilo")
use_style = st.checkbox("Usar modelo de estilo", value=False)
style_model_choice = st.selectbox("Escolha o modelo de estilo", list(style_models.keys()))
style_scheduler_choice = st.selectbox("Sampler", samplers, key="style_sampler")
style_strength = st.slider("Strength", 0.0, 1.0, 0.85, 0.05, key="style_strength")
style_guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 6.0, 0.5, key="style_guidance_scale")
style_steps = st.slider("Número de passos", 10, 100, 25, 1, key="style_steps")


# Estado para armazenar imagens geradas
if "base_outputs" not in st.session_state:
    st.session_state.base_outputs = []

if "styled_outputs" not in st.session_state:
    st.session_state.styled_outputs = []

# Gerar uma imagem base por vez
if st.button("Gerar imagem base"):
    input_image = None
    if uploaded_image:
        input_image = Image.open(uploaded_image).convert("RGB").resize((768, 512))

    if use_base:
        base_pipe = load_pipeline(base_models[base_model_choice], img2img=input_image is not None, scheduler_name=base_scheduler_choice)
        base_img = generate_image(base_pipe, prompt, negative_prompt, input_image, base_strength, base_guidance_scale, base_steps)
        st.session_state.base_outputs = [base_img] 

# Mostrar última imagem base
if st.session_state.base_outputs:
    st.subheader("Imagem base")
    base_img = st.session_state.base_outputs[-1]
    st.image(base_img, caption="Imagem base", use_container_width=True)
    buf = BytesIO()
    base_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("Baixar imagem base", buf, file_name="base_output.png", mime="image/png")

# Aplicar estilo na última imagem base OU diretamente na imagem enviada
style_input_image = None
if st.session_state.base_outputs:
    style_input_image = st.session_state.base_outputs[-1]
elif uploaded_image:
    style_input_image = Image.open(uploaded_image).convert("RGB").resize((768, 512))

if use_style and style_input_image:
    if st.button("Aplicar estilo"):
        if style_model_choice == "Ghibli Diffusion":
            prompt_with_prefix = "Ghibli Art, " + prompt
        elif style_model_choice == "Van Gogh Diffusion":
            prompt_with_prefix = "lvngvncnt, " + prompt
        elif style_model_choice == "disney-pixar-cartoon":
            prompt_with_prefix = "disney style, " + prompt
        else:
            prompt_with_prefix = prompt

        style_pipe = load_pipeline(style_models[style_model_choice], img2img=True, scheduler_name=style_scheduler_choice)
        final_image = generate_image(style_pipe, prompt_with_prefix, negative_prompt, style_input_image, style_strength, style_guidance_scale, style_steps)
        st.session_state.styled_outputs = [final_image] 

# Mostrar última imagem estilizada
if st.session_state.styled_outputs:
    st.subheader("Imagem estilizada")
    styled_img = st.session_state.styled_outputs[-1]
    st.image(styled_img, caption="Imagem estilizada", use_container_width=True)
    buf = BytesIO()
    styled_img.save(buf, format="PNG")
    buf.seek(0)
    st.download_button("Baixar imagem estilizada", buf, file_name="styled_output.png", mime="image/png")


