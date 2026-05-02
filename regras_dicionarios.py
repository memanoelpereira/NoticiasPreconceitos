# regras_dicionarios.py

TERMOS_ALVO_SPACY = [
    "preconceito", "discriminacao", "estereotipo", "preconceito regional", "estereotipo regional", "estigma territorial", "estigma", "desumanizacao", "racismo", "misoginia",
    "homofobia", "transfobia", "xenofobia", "aporofobia", "capacitismo", "antissemitismo", "islamofobia",
    "violencia simbolica", "discurso de odio", "microagressao", "minorias", "desigualdade", "exclusao",
    "intolerancia religiosa", "injuria racial", "humilhacao", "segregacao", "ridicularizacao"
]

BLACKLIST_EXATA = {
    "inter", "cultura", "educacao", "opiniao", "noticias", "mundo", "brasil",
    "esportes", "colunistas", "+", "host", "ao vivo", "ideias", "saber", "jogada",
    "mais noticias", "ultimas noticias", "entretenimento", "politica & economia",
    "editoriais", "o que a folha pensa", "dn auto", "internacional", "politica",
    "nacional", "sustentabilidade", "justica", "economia", "saude", "tecnologia",
}

BLACKLIST_EDITORIAL = [
    "editoriais", "o que a folha pensa", "ao vivo", "colunistas",
    "mais noticias", "ultimas noticias", "painel do leitor",
    "ideias", "saber", "jogada", "host", "checamos", "videos",
    "tendencias / debates", "politica & economia",
]

BLACKLIST_FRAGMENTOS = [
    "dn auto", "negocios automotivos", "faculdade de direito inova",
    "sucesso sorri para quem nao desiste", "a revolucao silenciosa do liberalismo",
    "bilhetagem em papel", "shoppings enfrentam queda de publico", "bbb 26",
    "aliados nao querem nem ouvir falar", "brb e governo do df",
    "volume de verbas federais destinadas", "relacao do cliente com a internet",
    "por que bilionarios estao transferindo",
]

BLACKLIST_ESPORTIVA = [
    "venceu", "vence", "empata", "derrota", "gols", "gol", "escalacao",
    "rodada", "tabela", "classificacao", "lesao", "mercado da bola",
    "onde assistir", "placar", "transfer ban", "saf", "mandante",
]



BLACKLIST_CULTURAL = [
    "moda", "colecao propria", "saude e bem-estar", "alimentacao",
    "hollywood", "filmes imperdiveis", "cultura e lazer", "donna",
    "divirta-se", "cinematerna", "casais", "divorcio", "casamento",
    "namoro", "relacionamento", "quartos separados", "intimidade",
    "fofoca", "celebridades", "famosos", "influenciador", "influenciadora"
]

BLACKLIST_ECONOMICA = [
    "ferrovia", "transnordestina", "usina", "geladeiras", "fabrica",
    "ativos comprados", "banco master", "itbi", "transacoes imobiliarias",
    "reforma laboral", "mercado aquecido", "patrimonio", "bilhetagem",
    "mobilidade digital", "verbas federais", "orcamento", "emprestimo",
    "fies", "cvm", "biocombustiveis", "divida publica", "falencia",
    "recuperacao judicial", "livraria cultura", "decretou falencia",
    "dividendos", "bolsa de valores", "ibovespa"
]

BLACKLIST_VIOLENCIA_GENERICA = [
    "confessa o crime", "acusado de matar", "barra de ferro",
    "a facadas", "assassinato", "ponto turistico",
]

GATILHOS_FORTES = [
    "racismo", "racista", "injuria racial", "ofensa racista",
    "homofobia", "homofob", "transfobia", "transfob",
    "xenofobia", "xenofob", "misoginia", "misogin",
    "machismo", "capacitismo", "capacitista",
    "preconceito", "preconceitu", "discriminac", "discriminacao",
    "estereotip", "estigma", "estigmatiza", "desumaniza", "animaliza",
    "intolerancia religiosa", "discurso de odio",
    "odio racial", "odio religioso",
    "lgbtfobia", "neonazi", "neonazista", "nazismo",
    "antissemitismo", "islamofobia", "aporofobia", "microagress",
    "segregacao", "segrega",
    "crime de racismo", "ataque racista", "canticos racistas",
    "torcida racista", "combate ao racismo",
    "violencia digital contra as mulheres",
    "violencia contra as mulheres",
    "cotas raciais", "politica de cotas",
    "demarcacao de terras", "injuria", "crime de odio",
]

GRUPOS_SOCIAIS = [
    "negros", "negro", "pretos", "preto",
    "indigenas", "indigena", "quilombola", "quilombolas",
    "mulheres", "mulher", "meninas",
    "imigrantes", "imigrante", "migrantes", "refugiados", "refugiado",
    "lgbt", "lgbtqia", "travesti", "travestis", "gay", "lesbica",
    "bissexual", "nao-binario",
    "deficiencia", "pcd", "autistas", "autista",
    "judeus", "muculmanos", "evangelicos", "religiosos", "religiosa",
    "povos originarios", "povos tradicionais",
    "afro-brasileiro", "afro-brasileira", "terreiro", "terreiros",
    "umbandista", "candomblecista",
    "mulher trans", "homem trans", "pessoa trans",
    "populacao negra", "populacao indigena",
    "comunidade quilombola", "comunidade lgbt",
    "minoria", "minorias",
]

CONTEXTOS_SENSIVEIS = [
    "futebol", "esporte", "esportes", "estadio", "torcida", "torcedor",
    "torcedores", "clube", "campeonato", "selecao", "jogador", "jogadora",
    "atleta", "arbitragem", "cbf", "escola", "universidade", "campus", "faculdade", "sala de aula",
    "igreja", "templo", "terreiro", "culto", "candomble",
    "umbanda", "mesquita", "sinagoga", "hijab", "turbante",
    "periferia", "favela", "favelas", "cultura periferica",
    "funk", "rap", "hip hop", "samba", "sarau", "batalha de rima",
    "folguedo", "folguedos", "festa popular", "festas populares",
    "cultura popular", "tradicao popular", "tradicoes populares",
    "arte", "artes", "artista", "espetaculo", "musica", "show",
    "cinema", "teatro", "danca", "lazer popular", "area de lazer",
    "indigena", "quilombola", "povos originarios",
    "vestimenta", "roupa", "traje", "costume", "tradicao",
    "pratica cultural", "modo de vida", "axe",
]

VERBOS_CONFLITO = [
    "proibe", "proibido", "proibida", "barra", "barrado", "barrada",
    "impede", "impedido", "impedida", "ridiculariza", "ridicularizado",
    "debocha", "deboche", "hostiliza", "hostilidade",
    "ataca", "atacado", "atacada", "ofende", "ofensa", "insulta", "insulto",
    "exclui", "exclusao", "criminaliza", "criminalizado", "criminalizada",
    "constrange", "constrangido", "constrangida",
    "humilha", "humilhado", "humilhada",
    "persegue", "perseguicao", "denuncia",
    "ameacas", "ameaca", "ameacado", "ameacada",
    "alvo de ataques", "alvo de ofensas",
    "relata preconceito", "pede combate",
    "combate a homofobia", "intolerancia contra",
    "ataque motivado por", "motivado por odio",
    "vitima de", "protesta", "protesto", "abandono", "abandonado",
    "marginalizacao", "violacao",
]

EXPRESSOES_ESPECIFICAS = [
    "combate global ao racismo", "avancos dos indigenas",
    "demarcacao", "ameacas e violencia",
    "violencia em condominio", "denuncia ameacas",
    "enfrentados na raiz", "lei de cotas",
    "acoes afirmativas", "reparacao historica",
    "violacao de direitos", "protecao de direitos",
    "direitos humanos", "genocidio", "apartheid",
]

TEMAS_POPULARES = [
    "futebol", "esporte", "esportes", "musica", "show", "espetaculo",
    "arte", "artes", "cinema", "teatro", "danca",
    "funk", "rap", "hip hop", "samba", "sarau",
    "folguedo", "folguedos", "festa popular", "festas populares",
    "cultura popular", "lazer popular", "area de lazer"
]

MARCADORES_SOCIAIS_POPULARES = [
    "racismo", "racista", "injuria racial", "homofobia", "transfobia",
    "xenofobia", "misoginia", "machismo", "preconceito", "discriminacao",
    "estigma", "segregacao", "odio", "intolerancia",
    "denuncia", "protesta", "protesto", "hostilidade", "ridiculariza",
    "ofensa", "insulto", "ataque", "ameaca", "alvo de criticas",
    "abandono", "abandonado", "exclusao", "marginalizacao", "violacao"
]

TEMAS_POPULARES_SENSIVEIS = [
    "futebol", "torcida", "torcedor", "jogador", "jogadora",
    "cultura popular", "festa popular", "festas populares",
    "folguedo", "folguedos", "funk", "rap", "hip hop", "samba",
    "espetaculo", "musica", "arte", "artes", "cinema", "teatro",
    "lazer popular", "area de lazer"
]

MARCADORES_POPULARES_ESTRITOS = [
    "racismo", "racista", "injuria racial", "homofobia", "transfobia",
    "xenofobia", "misoginia", "machismo", "preconceito", "discriminacao",
    "estigma", "segregacao", "intolerancia", "denuncia", "hostilidade",
    "ridiculariza", "ofensa", "insulto", "ataque", "ameaca",
    "abandono", "abandonado", "marginalizacao", "violacao"
]

CATEGORIAS_PUBLICAS = {
    "Racismo e discriminacao racial": ["racismo", "racista", "injuria racial", "ofensa racista", "discriminacao racial", "crime de racismo", "odio racial", "negro", "negra", "pretos", "pretas", "populacao negra", "cotas raciais", "acoes afirmativas", "branquitude"],
    "Genero, misoginia e violencia contra mulheres": ["misoginia", "misogin", "machismo", "sexismo", "feminicidio", "violencia contra mulher", "violencia contra mulheres", "assedio", "meninas", "mulher"],
    "LGBTQIA+ e LGBTfobia": ["homofobia", "homofob", "transfobia", "transfob", "lgbtfobia", "lgbt", "lgbtqia", "travesti", "travestis", "gay", "lesbica", "bissexual", "nao-binario", "mulher trans", "homem trans", "pessoa trans"],
    "Intolerancia religiosa e racismo religioso": ["intolerancia religiosa", "racismo religioso", "terreiro", "terreiros", "candomble", "umbanda", "mesquita", "sinagoga", "hijab", "ataque a terreiro", "religiao de matriz africana"],
    "Xenofobia, migracao e refugio": ["xenofobia", "xenofob", "imigrante", "imigrantes", "migrante", "migrantes", "refugiado", "refugiados", "migracao", "venezuelano", "haitiano", "boliviano"],
    "Povos indigenas, quilombolas e comunidades tradicionais": ["indigena", "indigenas", "povos originarios", "quilombola", "quilombolas", "demarcacao", "terras indigenas", "comunidades tradicionais", "povos tradicionais", "yanomami", "guarani", "kaingang", "tupinamba"],
    "Capacitismo e deficiencia": ["capacitismo", "capacitista", "pessoa com deficiencia", "pcd", "deficiencia", "deficiente", "autista", "autistas", "autismo", "neurodivergente", "acessibilidade"],
    "Estereotipos e preconceito regional e territorial": [
        "preconceito regional", "preconceito territorial", "estereotipo regional",
        "estereotipos regionais", "estereotipo territorial", "estereotipos territoriais",
        "estigma territorial", "discriminacao regional", "discriminacao territorial",
        "xenofobia contra nordestinos", "preconceito contra nordestinos",
        "nordestino", "nordestina", "nordestinos", "nordestinas",
        "sotaque", "sertanejo", "sertaneja", "amazonida", "amazonidas",
        "amazonia", "amazonico", "amazonica", "belem", "regiao norte",
        "norte do brasil", "interiorano", "interiorana", "ribeirinho", "ribeirinha",
        "e so mato", "so mato"
    ],
    "Classe, pobreza e aporofobia": ["aporofobia", "pobre", "pobres", "morador de rua", "populacao em situacao de rua", "favela", "favelas", "periferia", "periferico", "exclusao social", "desigualdade"],
    "Estigma corporal, aparencia e gordofobia": ["gordofobia", "obesidade", "corpo", "aparencia", "padrao de beleza", "estetica", "humilhacao corporal", "peso", "gordo", "gorda"],
    "Esporte, cultura e lazer com discriminacao": ["futebol", "torcida", "torcedor", "estadio", "jogador", "jogadora", "atleta", "musica", "show", "espetaculo", "teatro", "cinema", "samba", "funk", "rap", "hip hop", "festa popular", "cultura popular", "lazer popular"],
    "Direitos, justica e politicas publicas": ["direitos humanos", "stf", "stj", "tribunal", "ministerio publico", "defensoria", "projeto de lei", "politica publica", "lei de cotas", "acoes afirmativas", "reparacao", "igualdade racial", "minorias"],
}

ENQUADRAMENTOS_DISCURSIVOS = {
    "Grupo como ameaca": ["ameaca", "risco", "perigo", "invasao", "invadem", "radical", "extremista", "terror", "baderna", "desordem", "crise migratoria"],
    "Criminalizacao ou suspeicao": ["crime", "criminoso", "prisao", "preso", "investigado", "policia", "suspeito", "trafico", "furto", "roubo", "vandalismo", "depredacao"],
    "Vitimizacao e violencia sofrida": ["vitima", "agredido", "agredida", "ataque", "atacado", "atacada", "ofensa", "injuria", "humilhado", "humilhada", "hostilizado", "ameacado"],
    "Sujeito de direitos e reparacao": ["direitos", "reparacao", "igualdade", "inclusao", "acessibilidade", "cotas", "acoes afirmativas", "demarcacao", "politica publica", "combate ao racismo"],
    "Agencia politica e resistencia": ["protesto", "protesta", "mobilizacao", "movimento", "denuncia", "reivindica", "resistencia", "lideranca", "organizacao", "manifestacao"],
    "Moralizacao ou responsabilizacao individual": ["culpa", "merito", "merece", "comportamento", "disciplina", "bons costumes", "familia", "vergonha", "decoro", "moral"],
    "Linguagem estrutural": ["estrutural", "historica", "historico", "desigualdade", "colonial", "colonialismo", "institucional", "sistemico", "sistemica", "segregacao"],
    "Invisibilizacao ou apagamento": ["invisivel", "apagamento", "silenciamento", "sem reconhecimento", "esquecido", "negligenciado", "subnotificacao", "subnotificado"],
}

FONTE_TIPO_REGRAS = {
    "midia_identitaria_direitos": ["alma_preta", "geledes", "midia_india", "genero_e_numero", "patricia_galvao", "catarinas", "cimi", "apib", "conaq", "conectas", "hrw", "amnistia", "ponte", "agencia_mural", "vozdas_comunidades", "rioonwatch", "correio_nago"],
    "jornalismo_investigativo": ["intercept", "agencia_publica", "reporter_brasil", "de_olho_nos_ruralistas"],
    "fonte_institucional": ["gov", "senado", "camara", "stf", "stj", "tse", "agu", "mpf", "onu"],
    "fact_checker": ["lupa", "aos_fatos", "verifica", "comprova", "boatos"],
    "midia_religiosa": ["gospel", "pleno", "cristao", "guiame", "cnbb", "vatican"],
    "midia_internacional": ["bbc", "dw", "rfi", "france24", "euronews", "xinhua", "voa", "publico_pt", "nacla", "celag"],
}

REGIAO_FONTE_REGRAS = {
    "Norte": ["_AC", "_AP", "_AM", "_PA", "_RO", "_RR", "_TO", "Amazonia", "Acre", "Amapa", "Para"],
    "Nordeste": ["_AL", "_BA", "_CE", "_MA", "_PB", "_PE", "_PI", "_RN", "_SE", "Nordeste", "Bahia"],
    "Centro-Oeste": ["_DF", "_GO", "_MT", "_MS", "Braziliense", "Brasilia"],
    "Sudeste": ["_ES", "_MG", "_RJ", "_SP", "Folha_SP", "Estadao_SP", "O_Globo"],
    "Sul": ["_PR", "_RS", "_SC", "Parana", "Zero_Hora", "Sul21"],
}

STOPWORDS_CASO = {"a", "o", "as", "os", "um", "uma", "de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas", "por", "para", "com", "sem", "sobre", "entre", "apos", "que", "e", "ou", "ao", "aos", "pela", "pelo", "pelas", "pelos", "se", "sua", "seu", "suas", "seus", "mais", "menos", "novo", "nova", "diz", "dizem", "contra", "como"}

# ============================================================
# Classificação analítica v2 — camada substantiva centralizada
# ============================================================
# Esta camada NÃO substitui automaticamente CATEGORIAS_PUBLICAS nem
# ENQUADRAMENTOS_DISCURSIVOS. Ela organiza uma taxonomia revisada para ser
# aplicada pelo pipeline em colunas comparativas (_v2), permitindo auditoria
# antes de promover a nova classificação para os campos principais.

VERSAO_CLASSIFICACAO_ANALITICA_ATUAL = "v2_classificacao_analitica_territorial"

PESOS_CLASSIFICACAO_V2 = {
    # Peso do campo em que o termo aparece.
    "titulo": 3.0,
    "resumo": 2.0,
    "texto_completo": 1.0,

    # Peso do tipo de evidência dentro de cada categoria.
    "termos_explicitos": 3.0,
    "grupos": 2.5,
    "contextos": 1.4,
    "conflitos": 1.6,
    "expressoes": 2.2,
    "direitos_politicas": 1.8,

    # Penalização leve quando a evidência aparece apenas em termo muito amplo.
    "termo_amplo": 0.65,
}

# Famílias analíticas amplas. Servem para organizar a visualização e futuras
# auditorias, sem reduzir a categoria substantiva detalhada.
FAMILIAS_CATEGORIAS_V2 = {
    "Racismo e discriminacao racial": "Racismo, etnicidade e colonialidade",
    "Racismo religioso e intolerancia religiosa": "Racismo, etnicidade e colonialidade",
    "Povos indigenas, quilombolas e comunidades tradicionais": "Racismo, etnicidade e colonialidade",
    "Xenofobia, migracao e refugio": "Racismo, etnicidade e colonialidade",
    "Genero, misoginia e violencia contra mulheres": "Genero e sexualidade",
    "LGBTQIA+ e LGBTfobia": "Genero e sexualidade",
    "Capacitismo e deficiencia": "Corpo, funcionalidade e saude social",
    "Estigma corporal, aparencia e gordofobia": "Corpo, funcionalidade e saude social",
    "Estereotipos e preconceito regional e territorial": "Territorio, classe e desigualdade",
    "Classe social, pobreza e aporofobia": "Territorio, classe e desigualdade",
    "Etarismo, infancia, juventude e envelhecimento": "Geracoes e ciclo de vida",
    "Esporte, cultura e lazer com discriminacao": "Cultura, esporte e vida cotidiana",
    "Direitos, justica e politicas publicas": "Instituicoes, direitos e politicas publicas",
    "Estigma, exclusao e conflitos sociais": "Categoria residual",
}

# Cada categoria v2 separa tipos de evidência. O pipeline deve pontuar os termos
# por campo textual e por tipo de evidência, em vez de escolher apenas a primeira
# categoria encontrada.
CATEGORIAS_PUBLICAS_V2 = {
    "Racismo e discriminacao racial": {
        "termos_explicitos": [
            "racismo", "racista", "injuria racial", "ofensa racista",
            "discriminacao racial", "crime de racismo", "odio racial",
            "racismo estrutural", "racismo institucional", "racismo recreativo",
            "branquitude", "supremacismo branco", "neonazi", "neonazista",
        ],
        "grupos": [
            "negro", "negra", "negros", "negras", "preto", "preta",
            "pretos", "pretas", "populacao negra", "pessoa negra",
            "afro-brasileiro", "afro-brasileira", "afrodescendente",
        ],
        "contextos": [
            "escola", "universidade", "trabalho", "empresa", "loja", "shopping",
            "restaurante", "condominio", "futebol", "estadio", "torcida",
            "internet", "rede social", "policia", "justica",
        ],
        "conflitos": [
            "ofensa", "insulto", "humilhacao", "ataque", "agressao", "denuncia",
            "hostilidade", "constrangimento", "exclusao", "impedido", "barrado",
        ],
        "direitos_politicas": [
            "cotas raciais", "acoes afirmativas", "igualdade racial",
            "estatuto da igualdade racial", "reparacao", "politica de cotas",
        ],
        "expressoes": [
            "combate ao racismo", "canticos racistas", "torcida racista",
            "ataque racista", "fala racista", "comentario racista",
        ],
        "termos_amplos": ["racial"],
    },

    "Genero, misoginia e violencia contra mulheres": {
        "termos_explicitos": [
            "misoginia", "misogin", "machismo", "sexismo", "violencia de genero",
            "violencia politica de genero", "feminicidio", "assedio sexual",
            "importunacao sexual", "violencia domestica", "violencia contra mulher",
            "violencia contra mulheres",
        ],
        "grupos": ["mulher", "mulheres", "menina", "meninas", "feminista", "feministas"],
        "contextos": [
            "trabalho", "escola", "universidade", "politica", "camara", "senado",
            "internet", "rede social", "transporte", "casa", "familia", "esporte",
        ],
        "conflitos": [
            "ameaca", "agressao", "ataque", "assediada", "ofensa", "humilhacao",
            "perseguicao", "denuncia", "impedida", "desigualdade salarial",
        ],
        "direitos_politicas": [
            "lei maria da penha", "igualdade de genero", "delegacia da mulher",
            "politica para mulheres", "direitos das mulheres",
        ],
        "expressoes": [
            "violencia contra as mulheres", "combate a misoginia", "combate ao machismo",
            "mulheres na politica", "mulheres no esporte",
        ],
        "termos_amplos": ["mulher", "mulheres"],
    },

    "LGBTQIA+ e LGBTfobia": {
        "termos_explicitos": [
            "homofobia", "homofob", "transfobia", "transfob", "lgbtfobia",
            "lesbofobia", "bifobia", "LGBTfobia", "discriminacao por orientacao sexual",
            "discriminacao por identidade de genero",
        ],
        "grupos": [
            "lgbt", "lgbtqia", "travesti", "travestis", "gay", "gays",
            "lesbica", "lesbicas", "bissexual", "bissexuais", "nao-binario",
            "nao-binaria", "mulher trans", "homem trans", "pessoa trans",
            "pessoas trans", "queer",
        ],
        "contextos": [
            "escola", "universidade", "trabalho", "familia", "igreja", "politica",
            "banheiro", "esporte", "internet", "rede social", "saude",
        ],
        "conflitos": [
            "agressao", "ataque", "ofensa", "expulso", "expulsa", "barrado",
            "impedido", "impedida", "ameaca", "morte", "denuncia", "humilhacao",
        ],
        "direitos_politicas": [
            "casamento igualitario", "nome social", "retificacao de nome",
            "direitos lgbt", "direitos lgbtqia", "politica lgbt",
        ],
        "expressoes": [
            "parada lgbt", "orgulho lgbt", "cura gay", "banheiro unissex",
            "ideologia de genero", "combate a homofobia", "combate a transfobia",
        ],
        "termos_amplos": ["gay", "lgbt"],
    },

    "Racismo religioso e intolerancia religiosa": {
        "termos_explicitos": [
            "intolerancia religiosa", "racismo religioso", "islamofobia",
            "antissemitismo", "odio religioso", "discriminacao religiosa",
        ],
        "grupos": [
            "candomble", "umbanda", "terreiro", "terreiros", "religiao de matriz africana",
            "povo de santo", "orixa", "umbandista", "candomblecista", "muculmano",
            "muculmanos", "judeu", "judeus", "evangelico", "catolico", "religiosos",
        ],
        "contextos": [
            "templo", "igreja", "terreiro", "mesquita", "sinagoga", "escola",
            "universidade", "internet", "politica", "comunidade",
        ],
        "conflitos": [
            "ataque", "depredacao", "incendio", "ofensa", "ameaaca", "ameaca",
            "invasao", "destruicao", "proibido", "impedido", "hostilidade", "denuncia",
        ],
        "direitos_politicas": [
            "liberdade religiosa", "laicidade", "estado laico", "direito ao culto",
        ],
        "expressoes": [
            "ataque a terreiro", "terreiro atacado", "racismo contra religioes de matriz africana",
            "combate a intolerancia religiosa",
        ],
        "termos_amplos": ["religiao", "religioso", "religiosa"],
    },

    "Xenofobia, migracao e refugio": {
        "termos_explicitos": [
            "xenofobia", "xenofob", "discriminacao contra imigrantes",
            "odio contra imigrantes", "crise migratoria",
        ],
        "grupos": [
            "imigrante", "imigrantes", "migrante", "migrantes", "refugiado",
            "refugiados", "refugiada", "refugiadas", "venezuelano", "venezuelana",
            "haitiano", "haitiana", "boliviano", "boliviana", "africano", "africana",
        ],
        "contextos": [
            "fronteira", "abrigo", "trabalho", "escola", "saude", "moradia",
            "documentacao", "regularizacao", "politica", "cidade",
        ],
        "conflitos": [
            "expulso", "expulsa", "barrado", "barrada", "ofensa", "ataque",
            "agressao", "exploracao", "trabalho analogo", "denuncia", "hostilidade",
        ],
        "direitos_politicas": [
            "refugio", "asilo", "regularizacao migratoria", "direitos dos migrantes",
            "acolhimento", "politica migratoria",
        ],
        "expressoes": ["combate a xenofobia", "acolhimento de refugiados", "crise de refugiados"],
        "termos_amplos": ["migracao", "fronteira"],
    },

    "Povos indigenas, quilombolas e comunidades tradicionais": {
        "termos_explicitos": [
            "anti-indigena", "racismo anti-indigena", "violencia contra indigenas",
            "violencia contra quilombolas", "genocidio indigena", "etnocidio",
        ],
        "grupos": [
            "indigena", "indigenas", "povos originarios", "povo originario",
            "quilombola", "quilombolas", "comunidades tradicionais", "povos tradicionais",
            "yanomami", "guarani", "kaiowa", "kaingang", "tupinamba", "munduruku",
            "ribeirinho", "ribeirinha", "extrativista",
        ],
        "contextos": [
            "terra indigena", "terras indigenas", "quilombo", "territorio",
            "garimpo", "madeireiro", "agronegocio", "demarcacao", "conflito fundiario",
            "amazonia", "saude indigena", "educacao indigena",
        ],
        "conflitos": [
            "invasao", "ameaca", "assassinato", "ataque", "violencia", "expulsao",
            "contaminacao", "garimpo ilegal", "desmatamento", "denuncia", "conflito",
        ],
        "direitos_politicas": [
            "demarcacao", "marco temporal", "direitos territoriais", "consulta previa",
            "funai", "sesai", "territorio quilombola", "titulacao quilombola",
        ],
        "expressoes": [
            "demarcacao de terras", "marco temporal", "terra indigena invadida",
            "ataque a comunidade quilombola",
        ],
        "termos_amplos": ["indigena", "quilombola"],
    },

    "Capacitismo e deficiencia": {
        "termos_explicitos": [
            "capacitismo", "capacitista", "discriminacao contra pessoa com deficiencia",
            "barreira de acessibilidade", "ableismo",
        ],
        "grupos": [
            "pessoa com deficiencia", "pessoas com deficiencia", "pcd", "deficiente",
            "deficientes", "autista", "autistas", "autismo", "neurodivergente",
            "cadeirante", "surdo", "surda", "cego", "cega",
        ],
        "contextos": [
            "escola", "universidade", "trabalho", "transporte", "saude", "concurso",
            "loja", "shopping", "evento", "acessibilidade", "servico publico",
        ],
        "conflitos": [
            "barrado", "impedido", "excluido", "ofensa", "humilhacao", "recusado",
            "negado", "falta de acessibilidade", "denuncia", "constrangimento",
        ],
        "direitos_politicas": [
            "lei brasileira de inclusao", "lbi", "acessibilidade", "educacao inclusiva",
            "cota pcd", "direitos da pessoa com deficiencia",
        ],
        "expressoes": ["combate ao capacitismo", "falta de acessibilidade", "inclusao de pessoas com deficiencia"],
        "termos_amplos": ["deficiencia", "acessibilidade"],
    },

    "Estereotipos e preconceito regional e territorial": {
        "termos_explicitos": [
            "preconceito regional", "preconceito territorial", "discriminacao regional",
            "discriminacao territorial", "estigma territorial", "estigma regional",
            "xenofobia contra nordestinos", "preconceito contra nordestinos",
            "estereotipo regional", "estereotipos regionais",
            "estereotipo territorial", "estereotipos territoriais",
            "estereotipos sobre belem", "estereotipo sobre belem",
            "estereotipos sobre a amazonia", "estereotipo sobre a amazonia",
            "estereotipos sobre o norte", "estereotipo sobre o norte",
        ],
        "grupos": [
            "nordestino", "nordestina", "nordestinos", "nordestinas",
            "sertanejo", "sertaneja", "ribeirinho", "ribeirinha",
            "amazonida", "amazonidas", "amazônida", "amazônidas",
            "paraense", "paraenses", "belemense", "belemenses",
            "morador da amazonia", "moradores da amazonia",
            "morador do norte", "moradores do norte",
            "periferico", "periferica", "morador de favela", "moradores de favela",
        ],
        "contextos": [
            "sotaque", "regiao", "territorio", "interior", "capital", "cidade",
            "belem", "belém", "amazonia", "amazônia", "amazonico", "amazonica",
            "regiao norte", "norte do brasil", "para", "pará", "acre", "amapa",
            "amazonas", "rondonia", "roraima", "tocantins", "periferia", "favela",
            "comunidade", "moradia", "trabalho", "internet", "rede social", "politica",
        ],
        "conflitos": [
            "ofensa", "deboche", "ridicularizacao", "ridicularização", "humilhacao",
            "humilhação", "hostilidade", "exclusao", "exclusão", "criminalizacao",
            "criminalização", "denuncia", "denúncia", "ataque", "rebaixamento",
        ],
        "direitos_politicas": [
            "direito a cidade", "politica territorial", "urbanizacao", "moradia digna",
            "desenvolvimento regional", "desigualdade regional", "representacao regional",
        ],
        "expressoes": [
            "preconceito contra nordestinos", "discriminacao por sotaque", "estigma da favela",
            "e so mato", "é só mato", "so mato", "só mato",
            "estereotipos sobre belem", "estereótipos sobre belém",
            "estereotipos sobre a amazonia", "estereótipos sobre a amazônia",
            "estereotipos sobre o norte", "estereótipos sobre o norte",
        ],
        "termos_amplos": [
            "periferia", "favela", "comunidade", "amazonia", "amazônia",
            "belem", "belém", "norte", "territorio", "território",
        ],
    },

    "Classe social, pobreza e aporofobia": {
        "termos_explicitos": [
            "aporofobia", "preconceito de classe", "discriminacao por pobreza",
            "criminalizacao da pobreza", "higienismo", "exclusao social",
        ],
        "grupos": [
            "pobre", "pobres", "morador de rua", "moradores de rua",
            "populacao em situacao de rua", "sem teto", "sem-teto", "catador",
            "catadores", "trabalhador informal", "desempregado",
        ],
        "contextos": [
            "rua", "abrigo", "centro", "shopping", "transporte", "trabalho",
            "moradia", "assistencia social", "seguranca alimentar", "escola",
        ],
        "conflitos": [
            "expulsao", "remocao", "ofensa", "ataque", "violencia", "impedido",
            "barrado", "criminalizacao", "denuncia", "hostilidade", "humilhacao",
        ],
        "direitos_politicas": [
            "assistencia social", "bolsa familia", "politica de moradia", "renda basica",
            "seguranca alimentar", "direitos sociais",
        ],
        "expressoes": ["populacao em situacao de rua", "combate a aporofobia", "criminalizacao da pobreza"],
        "termos_amplos": ["pobreza", "desigualdade"],
    },

    "Estigma corporal, aparencia e gordofobia": {
        "termos_explicitos": [
            "gordofobia", "preconceito estetico", "estigma corporal", "humilhacao corporal",
            "discriminacao por aparencia", "padrao de beleza",
        ],
        "grupos": ["gordo", "gorda", "gordos", "gordas", "obeso", "obesa", "pessoa obesa"],
        "contextos": ["trabalho", "escola", "universidade", "moda", "saude", "internet", "rede social", "academia", "esporte"],
        "conflitos": ["ofensa", "ridicularizacao", "humilhacao", "exclusao", "discriminacao", "bullying", "denuncia"],
        "direitos_politicas": ["diversidade corporal", "inclusao", "saude sem estigma"],
        "expressoes": ["combate a gordofobia", "pressao estetica", "padrao corporal"],
        "termos_amplos": ["corpo", "aparencia", "peso"],
    },

    "Etarismo, infancia, juventude e envelhecimento": {
        "termos_explicitos": ["etarismo", "idadismo", "discriminacao por idade", "preconceito contra idosos"],
        "grupos": ["idoso", "idosa", "idosos", "idosas", "velho", "velha", "crianca", "criancas", "adolescente", "adolescentes", "jovem", "jovens"],
        "contextos": ["trabalho", "saude", "familia", "escola", "internet", "politica", "previdencia"],
        "conflitos": ["exclusao", "abandono", "violencia", "negligencia", "ofensa", "humilhacao", "denuncia"],
        "direitos_politicas": ["estatuto do idoso", "estatuto da crianca e do adolescente", "eca", "direitos da pessoa idosa"],
        "expressoes": ["combate ao etarismo", "violencia contra idosos", "abandono de idosos"],
        "termos_amplos": ["juventude", "envelhecimento"],
    },

    "Esporte, cultura e lazer com discriminacao": {
        "termos_explicitos": [
            "racismo no futebol", "homofobia no futebol", "discriminacao no esporte",
            "preconceito no esporte", "intolerancia no esporte",
        ],
        "grupos": [
            "jogador negro", "jogadora negra", "atleta negro", "atleta negra",
            "torcedor", "torcida", "artista negro", "artista negra", "artista lgbt",
            "mulher no esporte", "mulheres no esporte",
        ],
        "contextos": [
            "futebol", "estadio", "torcida", "clube", "campeonato", "cbf",
            "musica", "show", "espetaculo", "teatro", "cinema", "samba", "funk",
            "rap", "hip hop", "sarau", "festa popular", "cultura popular", "lazer popular",
        ],
        "conflitos": [
            "ofensa", "cantico", "canticos", "insulto", "ataque", "hostilidade",
            "denuncia", "punicao", "suspensao", "briga", "ameaca", "ridicularizacao",
        ],
        "direitos_politicas": ["campanha antirracista", "protocolo antirracista", "inclusao no esporte", "diversidade cultural"],
        "expressoes": [
            "canticos racistas", "torcida racista", "racismo em estadio",
            "homofobia no futebol", "combate ao racismo no esporte",
        ],
        "termos_amplos": ["futebol", "musica", "show", "arte"],
    },

    "Direitos, justica e politicas publicas": {
        "termos_explicitos": [
            "direitos humanos", "politica publica", "politicas publicas", "acoes afirmativas",
            "reparacao", "igualdade", "inclusao", "discriminacao institucional",
        ],
        "grupos": ["minoria", "minorias", "grupos vulneraveis", "populacao vulneravel"],
        "contextos": [
            "stf", "stj", "tribunal", "ministerio publico", "defensoria", "camara",
            "senado", "governo", "prefeitura", "conselho", "comissao", "onu",
        ],
        "conflitos": ["denuncia", "acao", "processo", "julgamento", "condenacao", "recurso", "violacao", "descumprimento"],
        "direitos_politicas": [
            "lei de cotas", "estatuto", "plano nacional", "programa", "projeto de lei",
            "decisao judicial", "audiencia publica", "recomendacao", "resolucao",
        ],
        "expressoes": ["violacao de direitos", "protecao de direitos", "defesa de minorias", "garantia de direitos"],
        "termos_amplos": ["lei", "justica", "politica"],
    },

    "Estigma, exclusao e conflitos sociais": {
        "termos_explicitos": [
            "preconceito", "discriminacao", "estigma", "estigmatizacao", "estereotipo",
            "estereotipia", "exclusao", "segregacao", "desumanizacao", "animalizacao",
            "discurso de odio", "microagressao", "humilhacao", "intolerancia",
        ],
        "grupos": ["minoria", "minorias", "grupo vulneravel", "grupos vulneraveis"],
        "contextos": ["escola", "trabalho", "internet", "politica", "saude", "justica", "cidade"],
        "conflitos": ["ofensa", "ataque", "denuncia", "ameaca", "exclusao", "violacao", "hostilidade"],
        "direitos_politicas": ["direitos humanos", "igualdade", "inclusao"],
        "expressoes": ["combate ao preconceito", "combate a discriminacao", "discurso de odio"],
        "termos_amplos": ["conflito social"],
    },
}

ENQUADRAMENTOS_DISCURSIVOS_V2 = {
    "Grupo como ameaca": {
        "termos": [
            "ameaca", "risco", "perigo", "invasao", "invadem", "baderna",
            "desordem", "radical", "extremista", "terror", "terrorismo",
            "crise migratoria", "contaminacao", "degeneracao",
        ],
        "familia": "estigmatizante",
        "direcao": "negativa",
    },
    "Criminalizacao ou suspeicao": {
        "termos": [
            "crime", "criminoso", "criminosa", "suspeito", "suspeita", "prisao",
            "preso", "presa", "investigado", "trafico", "furto", "roubo",
            "vandalismo", "depredacao", "facção", "faccao", "policia",
        ],
        "familia": "estigmatizante",
        "direcao": "negativa",
    },
    "Vitimizacao e violencia sofrida": {
        "termos": [
            "vitima", "vitimas", "agredido", "agredida", "ataque", "atacado",
            "atacada", "ofensa", "injuria", "humilhado", "humilhada", "hostilizado",
            "hostilizada", "ameacado", "ameacada", "morto", "morta", "ferido", "ferida",
        ],
        "familia": "dano_sofrido",
        "direcao": "denuncia",
    },
    "Sujeito de direitos e reparacao": {
        "termos": [
            "direitos", "direitos humanos", "reparacao", "igualdade", "inclusao",
            "acessibilidade", "cotas", "acoes afirmativas", "demarcacao",
            "politica publica", "garantia", "protecao", "estatuto",
        ],
        "familia": "direitos",
        "direcao": "positiva",
    },
    "Agencia politica e resistencia": {
        "termos": [
            "protesto", "protesta", "mobilizacao", "movimento", "denuncia",
            "reivindica", "resistencia", "lideranca", "organizacao", "manifestacao",
            "coletivo", "marcha", "campanha", "ato publico",
        ],
        "familia": "agencia",
        "direcao": "positiva",
    },
    "Moralizacao ou responsabilizacao individual": {
        "termos": [
            "culpa", "merito", "merece", "comportamento", "disciplina",
            "bons costumes", "familia", "vergonha", "decoro", "moral", "imoral",
            "ideologia", "doutrinacao", "degeneracao",
        ],
        "familia": "moralizacao",
        "direcao": "ambivalente",
    },
    "Linguagem estrutural": {
        "termos": [
            "estrutural", "historica", "historico", "desigualdade", "colonial",
            "colonialismo", "institucional", "sistemico", "sistemica", "segregacao",
            "vulnerabilidade", "subalternizacao", "interseccionalidade",
        ],
        "familia": "estrutural",
        "direcao": "analitica",
    },
    "Invisibilizacao ou apagamento": {
        "termos": [
            "invisivel", "invisibilidade", "apagamento", "silenciamento",
            "sem reconhecimento", "esquecido", "esquecida", "negligenciado",
            "negligenciada", "subnotificacao", "subnotificado", "subnotificada",
        ],
        "familia": "apagamento",
        "direcao": "denuncia",
    },
    "Exotizacao ou folclorizacao": {
        "termos": [
            "exotico", "exotica", "folclore", "folclorico", "folclorica",
            "tribal", "curioso", "curiosidade", "pitoresco", "tradicao exotica",
        ],
        "familia": "estigmatizante",
        "direcao": "ambivalente",
    },
}

# Versões achatadas para facilitar uso por funções simples do pipeline, se desejado.
CATEGORIAS_PUBLICAS_V2_FLAT = {
    categoria: sorted(set(
        termo
        for bloco in dados.values()
        if isinstance(bloco, list)
        for termo in bloco
    ))
    for categoria, dados in CATEGORIAS_PUBLICAS_V2.items()
}

ENQUADRAMENTOS_DISCURSIVOS_V2_FLAT = {
    nome: dados.get("termos", [])
    for nome, dados in ENQUADRAMENTOS_DISCURSIVOS_V2.items()
}
