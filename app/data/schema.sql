CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    perfil TEXT NOT NULL CHECK (perfil IN ('suporte', 'consultor')),
    senha_hash TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    tentativas_falhas INTEGER NOT NULL DEFAULT 0,
    bloqueado_até TEXT
);

CREATE TABLE IF NOT EXISTS importacao (
    id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL REFERENCES usuario (id_usuario),
    codigo_contrato_siprov TEXT NOT NULL,
    data_hora TEXT NOT NULL,
    total_linhas INTEGER NOT NULL,
    situacao TEXT NOT NULL CHECK (
        situacao IN ('em_validacao', 'pronta', 'enviada', 'parcial', 'concluida')
    ),
    modo_envio TEXT NOT NULL CHECK (modo_envio IN ('api', 'arquivo'))
);

CREATE TABLE IF NOT EXISTS linha_importacao (
    id_linha INTEGER PRIMARY KEY AUTOINCREMENT,
    id_importacao INTEGER NOT NULL REFERENCES importacao (id_importacao),
    numero_linha INTEGER NOT NULL,
    placa TEXT NOT NULL,
    plano TEXT NOT NULL,
    dados_json TEXT NOT NULL,
    situacao TEXT NOT NULL CHECK (
        situacao IN ('pendente', 'aprovada', 'com_erro', 'incluida', 'falhou')
    ),
    mensagem_erro TEXT
);
