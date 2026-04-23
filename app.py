import os
import html

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


FUSO_BRASIL = "America/Sao_Paulo"

st.set_page_config(
    page_title="Agregador de notícias sobre preconceitos",
    layout="wide"
)


def get_db_url() -> str:
    secrets_dict = {}
    try:
        secrets_dict = st.secrets.to_dict()
    except Exception:
        secrets_dict = {}

    if "SUPABASE_DB_URL" in secrets_dict:
        return secrets_dict["SUPABASE_DB_URL"]

    env_url = os.getenv("SUPABASE_DB_URL", "").strip()
    if env_url:
        st.sidebar.write("**Fonte da conexão:** variável de ambiente")
        st.sidebar.code(env_url[:80] + ("..." if len(env_url) > 80 else ""))
        return env_url

    raise RuntimeError("SUPABASE_DB_URL não configurada.")


@st.cache_resource
def get_engine():
    return create_engine(
        get_db_url(),
        pool_pre_ping=True,
        poolclass=NullPool,
    )


@st.cache_data(ttl=60)
def carregar_dados():
    try:
        with get_engine().connect() as conn:
            df_noticias = pd.read_sql(
                text("SELECT * FROM noticias ORDER BY data_coleta DESC"),
                conn
            )
            df_entidades = pd.read_sql(
                text("SELECT * FROM entidades"),
                conn
            )
        return df_noticias, df_entidades, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), str(e)


def safe_text(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    return html.escape(str(value))


def formatar_data_curta(value, somente_data: bool = False) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    try:
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return "—"

        if getattr(ts, "tzinfo", None) is None:
            ts = ts.tz_localize("UTC")

        ts = ts.tz_convert(FUSO_BRASIL)

        if somente_data:
            return ts.strftime("%Y-%m-%d")
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)


def categorizar_publicamente(row) -> str:
    titulo = str(row.get("titulo", "") or "").lower()
    resumo = str(row.get("resumo", "") or "").lower()
    texto_completo = str(row.get("texto_completo", "") or "").lower()
    texto = f"{titulo} {resumo} {texto_completo}"

    def tem(*termos):
        return any(t in texto for t in termos)

    if tem(
        "racismo", "racista", "injuria racial", "injúria racial",
        "ofensa racista", "discriminacao racial", "discriminação racial",
        "negro", "negra", "pretos", "pretas", "população negra", "populacao negra",
        "cotas raciais"
    ):
        return "Racismo e discriminação racial"

    if tem(
        "misoginia", "misóginia", "machismo", "sexismo",
        "violencia contra a mulher", "violência contra a mulher",
        "violencia contra mulheres", "violência contra mulheres",
        "feminicidio", "feminicídio"
    ):
        return "Gênero, misoginia e violência contra mulheres"

    if tem(
        "homofobia", "transfobia", "lgbtfobia", "lgbt", "lgbtqia",
        "travesti", "travestis", "gay", "gays", "lésbica", "lesbica",
        "bissexual", "não-binário", "nao-binario", "mulher trans", "homem trans",
        "pessoa trans"
    ):
        return "LGBTQIA+ e LGBTfobia"

    if tem(
        "intolerancia religiosa", "intolerância religiosa",
        "terreiro", "terreiros", "candomble", "candomblé", "umbanda",
        "mesquita", "sinagoga", "templo", "hijab",
        "ataque a terreiro"
    ):
        return "Intolerância religiosa"

    if tem(
        "xenofobia", "xenófobia", "imigrante", "imigrantes",
        "migrante", "migrantes", "refugiado", "refugiados",
        "migração", "migracao"
    ):
        return "Xenofobia, migração e refugiados"

    if tem(
        "indigena", "indígena", "indigenas", "indígenas",
        "quilombola", "quilombolas", "povos originarios", "povos originários",
        "demarcacao", "demarcação", "terras indígenas", "terras indigenas",
        "comunidades tradicionais", "comunidade tradicional"
    ):
        return "Povos indígenas, quilombolas e comunidades tradicionais"

    if tem(
        "capacitismo", "capacitista", "pessoa com deficiência",
        "pessoa com deficiencia", "pcd", "autista", "autistas",
        "deficiente", "deficiência", "deficiencia"
    ):
        return "Capacitismos"

    if tem(
        "futebol", "torcida", "torcedor", "torcedores", "estadio", "estádio",
        "jogador", "jogadora", "clube", "campeonato",
        "show", "espetaculo", "espetáculo", "musica", "música",
        "teatro", "cinema", "samba", "funk", "rap", "hip hop",
        "cultura popular", "festa popular", "lazer popular"
    ):
        return "Discriminação nos esportes, cultura e lazer"

    if tem(
        "justiça", "justica", "tribunal", "stf", "stj",
        "direitos humanos", "ministério público", "ministerio publico",
        "projeto de lei", "política pública", "politica publica",
        "ações afirmativas", "acoes afirmativas", "lei de cotas", "lei"
    ):
        return "Direitos humanos, justiça e políticas públicas"

    return "Estigma, exclusão e conflitos sociais"


if "noticia_id_aberta" not in st.session_state:
    st.session_state.noticia_id_aberta = None


def abrir_noticia(noticia_id: int):
    st.session_state.noticia_id_aberta = noticia_id


def fechar_noticia():
    st.session_state.noticia_id_aberta = None


col_a, col_b = st.columns([5, 1])
with col_a:
    st.title("Agregador de notícias sobre preconceitos")
with col_b:
    if st.button("Atualizar agora", key="btn_atualizar_agregador"):
        if "noticia_id_aberta" in st.session_state:
            st.session_state.noticia_id_aberta = None
        st.cache_data.clear()
        st.rerun()

df_noticias, df_entidades, erro_db = carregar_dados()

if erro_db:
    st.error(f"Erro ao conectar ao Supabase: {erro_db}")

if not df_noticias.empty and "data_coleta" in df_noticias.columns:
    df_noticias["data_coleta_fmt"] = df_noticias["data_coleta"].apply(formatar_data_curta)
    data_mais_recente = formatar_data_curta(df_noticias["data_coleta"].max())
    df_noticias["categoria_publica"] = df_noticias.apply(categorizar_publicamente, axis=1)
else:
    data_mais_recente = "—"

total_noticias = len(df_noticias)
total_entidades = len(df_entidades)

m1, m2, m3 = st.columns(3)
m1.metric("Notícias", total_noticias)
m2.metric("Entidades", total_entidades)
m3.metric("Última coleta (Brasil)", data_mais_recente)

# Layout base
if total_noticias > 50:
    QTD_COLUNAS = 4
    CSS_PAD = "10px"
    CSS_FONT_TITULO = "0.92rem"
    CSS_FONT_TAG = "0.68rem"
elif total_noticias > 20:
    QTD_COLUNAS = 4
    CSS_PAD = "12px"
    CSS_FONT_TITULO = "0.98rem"
    CSS_FONT_TAG = "0.75rem"
else:
    QTD_COLUNAS = 4
    CSS_PAD = "15px"
    CSS_FONT_TITULO = "1.05rem"
    CSS_FONT_TAG = "0.8rem"

css = f"""
<style>
.tile-card {{
    background-color: #2b3a4a;
    color: white;
    border-radius: 12px 12px 0 0;
    overflow: hidden;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    margin-bottom: 0 !important;
    border-left: 5px solid transparent;
}}
.tile-body {{
    padding: {CSS_PAD};
    display: flex;
    flex-direction: column;
}}
.fonte-tag {{
    font-size: {CSS_FONT_TAG};
    background: #1e2933;
    padding: 4px 6px;
    border-radius: 4px;
    align-self: flex-start;
    margin-bottom: 8px;
    width: 100%;
    display: flex;
    justify-content: space-between;
}}

.titulo-noticia {{
    font-weight: bold;
    font-size: {CSS_FONT_TITULO};
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 7;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.data-tag {{
    font-size: {CSS_FONT_TAG};
    color: #aaa;
    margin-top: auto;
    padding-top: 8px;
}}
div[data-testid="stButton"] > button.tile-open {{
    width: 100%;
    min-height: 2.35rem;
    margin-top: 0 !important;
    margin-bottom: 14px !important;
    border-radius: 0 0 12px 12px;
    border: none;
    background: #3d4e5f;
    color: white;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
}}
div[data-testid="stButton"] > button.tile-open:hover {{
    background: #4b6075;
    color: white;
}}
div[data-testid="stButton"] > button.tile-open p {{
    font-weight: 600;
}}
.overlay-meta {{
    color: #4b5563;
    font-size: 0.95rem;
    margin-bottom: 10px;
}}
.overlay-title {{
    font-size: 1.35rem;
    line-height: 1.35;
    font-weight: 700;
    margin-bottom: 14px;
}}
.overlay-badge {{
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: #eef2ff;
    color: #3730a3;
    font-size: 0.8rem;
    margin-right: 6px;
    margin-bottom: 6px;
}}
.overlay-badge-tecnica {{
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: #f3f4f6;
    color: #4b5563;
    font-size: 0.8rem;
    margin-right: 6px;
    margin-bottom: 6px;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

if df_noticias.empty:
    st.warning("Nenhuma notícia no banco ainda. Execute o pipeline primeiro.")
else:
    peso_entidades = df_entidades["texto"].value_counts().to_dict() if not df_entidades.empty else {}

    def calcular_impacto(noticia_id):
        if df_entidades.empty:
            return 1
        ents = df_entidades[df_entidades["noticia_id"] == noticia_id]["texto"]
        score = 1 + sum(peso_entidades.get(e, 0) for e in ents)
        return max(1, int(score))

    df_noticias["impacto"] = df_noticias["id"].apply(calcular_impacto)


    def altura_por_impacto(impacto: int) -> int:
        if impacto >= 12:
            return 270
        if impacto >= 8:
            return 235
        if impacto >= 5:
            return 205
        if impacto >= 3:
            return 180
        return 150

    df_noticias = df_noticias.sort_values(
        by=["impacto", "data_coleta"],
        ascending=[False, False]
    )

    cols = st.columns(QTD_COLUNAS)
    for pos, (_, row) in enumerate(df_noticias.iterrows()):
        impacto_val = int(row["impacto"])
        altura = altura_por_impacto(impacto_val)
        cor_borda = "#ff4b4b" if impacto_val >= 8 else "#ffb020" if impacto_val >= 4 else "#00d4ff"
        noticia_id = int(row["id"])

        with cols[pos % QTD_COLUNAS]:
            st.markdown(
                f"""
                <div class="tile-card" style="border-left-color: {cor_borda};">
                    <div class="tile-body" style="min-height: {altura}px;">
                        <div class="fonte-tag">
                            <span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:70%;">{safe_text(row['fonte'])}</span>
                            <span style="color:#ffb020;flex-shrink:0;">🔥 {impacto_val}</span>
                        </div>
                        <div class="titulo-noticia">{safe_text(row['titulo'])}</div>
                        <div class="data-tag">{safe_text(row.get('data_coleta_fmt', row['data_coleta']))}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.button(
                "Acompanhar notícia",
                key=f"abrir_{noticia_id}",
                on_click=abrir_noticia,
                args=(noticia_id,),
                type="secondary"
            )

    st.markdown(
        """
        <script>
        const buttons = window.parent.document.querySelectorAll('div[data-testid="stButton"] button');
        buttons.forEach(btn => {
          if (btn.innerText.trim() === 'Acompanhar notícia') {
            btn.classList.add('tile-open');
          }
        });
        </script>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    with st.expander("🕒 Linha do tempo das notícias"):
        df_tempo = df_noticias.copy()
        df_tempo["data_plot"] = pd.to_datetime(df_tempo["data_coleta"], errors="coerce")
        df_tempo = df_tempo.dropna(subset=["data_plot"])

        if not df_tempo.empty:
            if getattr(df_tempo["data_plot"].dt, "tz", None) is None:
                df_tempo["data_plot"] = df_tempo["data_plot"].dt.tz_localize("UTC")
            df_tempo["data_plot"] = df_tempo["data_plot"].dt.tz_convert(FUSO_BRASIL).dt.normalize()

        if df_tempo.empty:
            st.info("Não há datas válidas para montar a linha do tempo.")
        else:
            col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 2])

            with col_ctrl1:
                granularidade = st.selectbox(
                    "Granularidade",
                    options=["Diária", "Semanal", "Mensal"],
                    index=0,
                    key="timeline_granularidade"
                )

            with col_ctrl2:
                modo_linha = st.selectbox(
                    "Modo",
                    options=["Linha única", "Por categoria pública", "Por portal"],
                    index=0,
                    key="timeline_modo"
                )

            with col_ctrl3:
                fontes_disponiveis = sorted(
                    [f for f in df_tempo["fonte"].dropna().unique().tolist() if str(f).strip()]
                )
                filtro_fontes = st.multiselect(
                    "Filtrar portais",
                    options=fontes_disponiveis,
                    default=[],
                    key="timeline_fontes"
                )

            if filtro_fontes:
                df_tempo = df_tempo[df_tempo["fonte"].isin(filtro_fontes)]

            if df_tempo.empty:
                st.info("Os filtros atuais não retornaram notícias.")
            else:
                freq_map = {
                    "Diária": "D",
                    "Semanal": "W-MON",
                    "Mensal": "MS"
                }
                freq_escolhida = freq_map[granularidade]

                def preparar_serie_unica(df_base: pd.DataFrame, freq: str, granularidade_txt: str) -> pd.DataFrame:
                    serie = (
                        df_base
                        .set_index("data_plot")
                        .resample(freq)
                        .size()
                        .rename("Quantidade")
                        .reset_index()
                    )

                    if not serie.empty:
                        intervalo = pd.date_range(
                            start=serie["data_plot"].min(),
                            end=serie["data_plot"].max(),
                            freq=freq
                        )
                        serie = (
                            serie
                            .set_index("data_plot")
                            .reindex(intervalo, fill_value=0)
                            .rename_axis("data_plot")
                            .reset_index()
                        )

                    if granularidade_txt == "Mensal":
                        serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m")
                    else:
                        serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m-%d")

                    return serie

                def preparar_serie_categoria(df_base: pd.DataFrame, freq: str, coluna: str, nome_coluna: str,
                                             granularidade_txt: str) -> pd.DataFrame:
                    df_aux = df_base.copy()
                    df_aux[coluna] = df_aux[coluna].fillna("Não informado").astype(str).str.strip()
                    df_aux.loc[df_aux[coluna] == "", coluna] = "Não informado"

                    serie = (
                        df_aux
                        .groupby([pd.Grouper(key="data_plot", freq=freq), coluna])
                        .size()
                        .reset_index(name="Quantidade")
                        .rename(columns={coluna: nome_coluna})
                    )

                    if serie.empty:
                        return serie

                    categorias = sorted(serie[nome_coluna].dropna().unique().tolist())
                    datas = pd.date_range(
                        start=serie["data_plot"].min(),
                        end=serie["data_plot"].max(),
                        freq=freq
                    )

                    grade = pd.MultiIndex.from_product(
                        [datas, categorias],
                        names=["data_plot", nome_coluna]
                    )

                    serie = (
                        serie
                        .set_index(["data_plot", nome_coluna])
                        .reindex(grade, fill_value=0)
                        .reset_index()
                    )

                    if granularidade_txt == "Mensal":
                        serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m")
                    else:
                        serie["data_str"] = pd.to_datetime(serie["data_plot"]).dt.strftime("%Y-%m-%d")

                    return serie

                if modo_linha == "Linha única":
                    serie_tempo = preparar_serie_unica(df_tempo, freq_escolhida, granularidade)

                    fig_tempo = px.line(
                        serie_tempo,
                        x="data_str",
                        y="Quantidade",
                        markers=True,
                        title=f"Evolução temporal das notícias ({granularidade.lower()})"
                    )

                    tabela_exibicao = serie_tempo.copy()

                elif modo_linha == "Por categoria pública":
                    serie_tempo = preparar_serie_categoria(
                        df_tempo,
                        freq_escolhida,
                        "categoria_publica",
                        "Categoria pública",
                        granularidade
                    )

                    fig_tempo = px.line(
                        serie_tempo,
                        x="data_str",
                        y="Quantidade",
                        color="Categoria pública",
                        markers=True,
                        title=f"Evolução temporal por categoria pública ({granularidade.lower()})"
                    )

                    tabela_exibicao = serie_tempo.copy()

                else:
                    serie_tempo = preparar_serie_categoria(
                        df_tempo,
                        freq_escolhida,
                        "fonte",
                        "Portal",
                        granularidade
                    )

                    fig_tempo = px.line(
                        serie_tempo,
                        x="data_str",
                        y="Quantidade",
                        color="Portal",
                        markers=True,
                        title=f"Evolução temporal por portal ({granularidade.lower()})"
                    )

                    tabela_exibicao = serie_tempo.copy()

                fig_tempo.update_layout(
                    xaxis_title="Data",
                    yaxis_title="Número de notícias",
                    hovermode="x unified"
                )
                fig_tempo.update_xaxes(
                    type="category",
                    tickangle=-45
                )

                st.plotly_chart(
                    fig_tempo,
                    use_container_width=True,
                    key=f"plot_timeline_{granularidade}_{modo_linha}_{'_'.join(filtro_fontes) if filtro_fontes else 'todos'}"
                )

                if modo_linha == "Linha única":
                    total_periodo = int(tabela_exibicao["Quantidade"].sum())
                    pico = int(tabela_exibicao["Quantidade"].max()) if not tabela_exibicao.empty else 0
                    periodos_com_registro = int((tabela_exibicao["Quantidade"] > 0).sum())

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Períodos com registro", periodos_com_registro)
                    c2.metric("Pico no período", pico)
                    c3.metric("Total no período", total_periodo)
                else:
                    total_periodo = int(tabela_exibicao["Quantidade"].sum())
                    pico = int(tabela_exibicao["Quantidade"].max()) if not tabela_exibicao.empty else 0
                    n_series = int(tabela_exibicao.iloc[:, 1].nunique()) if not tabela_exibicao.empty else 0

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Séries exibidas", n_series)
                    c2.metric("Pico em uma série", pico)
                    c3.metric("Total no período", total_periodo)

                with st.expander("Ver tabela da série temporal"):
                    tabela_exibicao = tabela_exibicao.copy()

                    if modo_linha == "Linha única":
                        st.dataframe(
                            tabela_exibicao[["data_str", "Quantidade"]].rename(columns={"data_str": "Data"}),
                            use_container_width=True,
                            hide_index=True
                        )
                    elif modo_linha == "Por categoria pública":
                        st.dataframe(
                            tabela_exibicao[["data_str", "Categoria pública", "Quantidade"]].rename(columns={"data_str": "Data"}),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.dataframe(
                            tabela_exibicao[["data_str", "Portal", "Quantidade"]].rename(columns={"data_str": "Data"}),
                            use_container_width=True,
                            hide_index=True
                        )

    with st.expander("📊 Estatística dos Portais"):
        stats_fonte = df_noticias["fonte"].value_counts().reset_index()
        stats_fonte.columns = ["Portal", "Quantidade"]
        fig = px.bar(
            stats_fonte,
            x="Portal",
            y="Quantidade",
            title="Volume de notícias por fonte"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="plot_estatistica_portais"
        )

    with st.expander("🏷️ Distribuição por categoria pública"):
        stats_cat = df_noticias["categoria_publica"].value_counts().reset_index()
        stats_cat.columns = ["Categoria pública", "Quantidade"]
        fig_cat = px.bar(
            stats_cat,
            x="Categoria pública",
            y="Quantidade",
            title="Distribuição das notícias por categoria pública"
        )
        fig_cat.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(
            fig_cat,
            use_container_width=True,
            key="plot_categorias_publicas"
        )

    with st.expander("🎯 Temas e personagens (NER)"):
        if not df_entidades.empty:
            stats_temas = df_entidades["texto"].value_counts().head(20).reset_index()
            stats_temas.columns = ["Entidade", "Frequência"]
            fig2 = px.bar(
                stats_temas,
                y="Entidade",
                x="Frequência",
                orientation="h",
                title="Top 20 entidades mais frequentes"
            )
            fig2.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(
                fig2,
                use_container_width=True,
                key="plot_top_entidades"
            )
        else:
            st.info("Ainda não há entidades extraídas para exibir.")

if st.session_state.noticia_id_aberta is not None and not df_noticias.empty:
    selecionada = df_noticias[df_noticias["id"] == st.session_state.noticia_id_aberta]
    entidades_rel = pd.DataFrame()
    if not df_entidades.empty:
        entidades_rel = df_entidades[
            df_entidades["noticia_id"] == st.session_state.noticia_id_aberta
        ].copy()

    if not selecionada.empty:
        row = selecionada.iloc[0]

        @st.dialog("Notícia", width="large")
        def modal_noticia():
            st.markdown(
                f'<div class="overlay-meta">{safe_text(row["fonte"])} · {safe_text(formatar_data_curta(row["data_coleta"]))}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="overlay-title">{safe_text(row["titulo"])}</div>',
                unsafe_allow_html=True
            )

            badges = []
            if "categoria_publica" in row.index and pd.notna(row["categoria_publica"]):
                badges.append(f'<span class="overlay-badge">{safe_text(row["categoria_publica"])}</span>')

            if "classificacao" in row.index and pd.notna(row["classificacao"]):
                badges.append(f'<span class="overlay-badge-tecnica">triagem: {safe_text(row["classificacao"])}</span>')

            if "criterio_filtro" in row.index and pd.notna(row["criterio_filtro"]):
                badges.append(f'<span class="overlay-badge-tecnica">critério: {safe_text(row["criterio_filtro"])}</span>')

            if "score_relevancia" in row.index and pd.notna(row["score_relevancia"]):
                try:
                    badges.append(f'<span class="overlay-badge-tecnica">score {float(row["score_relevancia"]):.3f}</span>')
                except Exception:
                    pass

            badges.append(f'<span class="overlay-badge-tecnica">impacto {int(row["impacto"])}</span>')
            st.markdown("".join(badges), unsafe_allow_html=True)

            texto_completo = None
            resumo = None
            url_fonte = None

            if "texto_completo" in row.index and pd.notna(row["texto_completo"]):
                texto_completo = str(row["texto_completo"]).strip()
            if "resumo" in row.index and pd.notna(row["resumo"]):
                resumo = str(row["resumo"]).strip()
            if "url_fonte" in row.index and pd.notna(row["url_fonte"]):
                url_fonte = str(row["url_fonte"]).strip()

            st.subheader("Texto da notícia")
            if texto_completo:
                st.markdown(texto_completo.replace("\n", "\n\n"))
            elif resumo:
                st.markdown(resumo)
                st.info("O banco tem apenas resumo para este item. O texto completo não foi capturado nesta coleta.")
            else:
                st.info("Este registro não tem texto completo armazenado. Para itens antigos, isso é esperado até uma nova coleta com o pipeline atualizado.")

            if url_fonte:
                st.link_button("Abrir fonte original", url_fonte)

            with st.expander("Mostrar metadados"):
                meta_cols = [
                    "id", "fonte", "data_coleta", "categoria_publica",
                    "classificacao", "criterio_filtro", "score_relevancia",
                    "url_fonte", "resumo"
                ]
                meta = {}
                for col in meta_cols:
                    if col in row.index:
                        value = row[col]
                        if col == "data_coleta" and not pd.isna(value):
                            meta[col] = formatar_data_curta(value)
                        else:
                            meta[col] = "—" if pd.isna(value) else value
                st.json(meta)

                st.markdown("**Entidades relacionadas**")
                if not entidades_rel.empty:
                    entidades_rel_ordenadas = entidades_rel.sort_values(by="tipo")
                    st.dataframe(
                        entidades_rel_ordenadas[["texto", "tipo"]].rename(
                            columns={"texto": "Entidade", "tipo": "Tipo"}
                        ),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.write("Nenhuma entidade extraída para este item.")

        modal_noticia()