# regras_dicionarios.py

TERMOS_ALVO_SPACY = [
    "preconceito", "discriminacao", "estereotipo", "estigma", "desumanizacao", "racismo", "misoginia",
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
    "Preconceito regional e territorial": ["nordestino", "nordestina", "nordestinos", "ant nordestino", "preconceito regional", "sotaque", "sertanejo", "amazonida", "interiorano", "ribeirinho"],
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