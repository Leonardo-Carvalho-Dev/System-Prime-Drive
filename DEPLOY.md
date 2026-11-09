# Implantação em produção

## Deploy atual: Render (ambiente de demonstração pública)

Para a entrega da Atividade 3, o MVP está publicado no [Render](https://render.com),
usando o Blueprint [`render.yaml`](render.yaml) deste repositório — sem precisar
configurar nada manualmente além das variáveis de ambiente.

**Como foi feito:**
1. Conta gratuita no Render, conectada à conta do GitHub (`Leonardo-Carvalho-Dev`).
2. **New +** → **Blueprint** → selecionar o repositório `System-Prime-Drive`. O Render lê
   o `render.yaml` e já propõe o serviço `importafrota-prime-drive` (plano Free, Python,
   `pip install -r requirements.txt`, `gunicorn 'app:create_app()' --bind 0.0.0.0:$PORT`),
   com health check em `/saude`.
3. Variáveis de ambiente definidas pelo Blueprint: `SECRET_KEY` (gerada automaticamente
   pelo Render, nunca digitada por mim), `SIPROV_MODE=fake` (nunca testar contra contrato
   real, regra 4 do `CLAUDE.md`), `SESSION_COOKIE_SECURE=true`, `DATABASE_PATH`.
4. Deploy automático a cada push na `main` (CI do GitHub Actions continua rodando os
   testes antes; o Render só builda/sobe depois).
5. Usuário de demonstração criado uma vez, via aba **Shell** do próprio serviço no Render:
   ```bash
   python criar_usuario.py demo-avaliador suporte
   ```
   (usuário e senha fictícios, só para o avaliador navegar pelo sistema — nunca dado real).

**Limitação conhecida:** o plano Free do Render não tem disco persistente — o arquivo
SQLite é recriado a cada deploy/reinício do serviço (ele dorme após ~15 min sem uso e
perde o estado ao acordar). Isso é aceitável aqui porque todos os dados usados em
demonstração são fictícios (regra 1 do `CLAUDE.md`); para produção real, trocar por um
disco persistente do Render (plano pago) ou um banco gerenciado.

**Monitoramento:** um monitor HTTP gratuito no [UptimeRobot](https://uptimerobot.com)
verifica `GET /saude` a cada 5 minutos; alerta por e-mail quando o status muda para
*DOWN* (ver print em anexo na entrega).

---

## Alternativa: servidor Linux próprio (Gunicorn + Nginx)

Guia genérico para uma instância Linux pequena (testado mentalmente contra Ubuntu
22.04/24.04 LTS). Ajuste nomes de usuário, domínio e caminhos conforme o servidor real.
Use este caminho quando houver um domínio e um servidor próprios — o deploy no Render
acima cobre a necessidade atual de uma URL pública para avaliação.

## 1. Pré-requisitos no servidor

- Ubuntu 22.04 ou 24.04 LTS, acesso root/sudo.
- Um domínio (ou subdomínio) apontando o DNS para o IP do servidor.
- Portas 80 e 443 liberadas no firewall/security group.

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv nginx certbot python3-certbot-nginx git
```

## 2. Criar o usuário de sistema e clonar o repositório

```bash
sudo adduser --system --group --home /opt/importafrota importafrota
sudo -u importafrota git clone https://github.com/Leonardo-Carvalho-Dev/System-Prime-Drive.git /opt/importafrota/app
cd /opt/importafrota/app
sudo -u importafrota python3.12 -m venv .venv
sudo -u importafrota .venv/bin/pip install -r requirements.txt
```

## 3. Configurar o `.env` de produção

```bash
sudo -u importafrota cp .env.example .env
sudo -u importafrota nano .env
```

Preencha (nunca commitar este arquivo):
- `SECRET_KEY`: valor aleatório forte (ex.: `python3 -c "import secrets; print(secrets.token_hex(32))"`).
- `SIPROV_MODE=real`, `SIPROV_USUARIO`, `SIPROV_SENHA`, `SIPROV_COD_LOJA`: credenciais reais do Siprov.
- `DATABASE_PATH=/opt/importafrota/dados/importafrota.db` (fora da pasta do código, para sobreviver a deploys).
- `SESSION_COOKIE_SECURE=true` (exige HTTPS — já configurado pelo Nginx/Certbot abaixo).

```bash
sudo -u importafrota mkdir -p /opt/importafrota/dados
```

## 4. Criar os usuários iniciais

```bash
cd /opt/importafrota/app
sudo -u importafrota .venv/bin/python criar_usuario.py ingrid suporte
# repita para cada consultor
```

## 5. Serviço systemd (Gunicorn)

`/etc/systemd/system/importafrota.service`:

```ini
[Unit]
Description=ImportaFrota Prime Drive (Gunicorn)
After=network.target

[Service]
User=importafrota
Group=importafrota
WorkingDirectory=/opt/importafrota/app
EnvironmentFile=/opt/importafrota/app/.env
ExecStart=/opt/importafrota/app/.venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 "app:create_app()"
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now importafrota
sudo systemctl status importafrota
```

## 6. Nginx como proxy reverso

`/etc/nginx/sites-available/importafrota`:

```nginx
server {
    listen 80;
    server_name SEU_DOMINIO;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 6M;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/importafrota /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 7. HTTPS (Let's Encrypt)

```bash
sudo certbot --nginx -d SEU_DOMINIO
```

O Certbot ajusta o bloco do Nginx para `listen 443 ssl` e redireciona `80 → 443`
automaticamente, além de agendar a renovação do certificado.

## 8. Backup diário do SQLite

Backup *online* e seguro (não copia o arquivo direto, para evitar corromper um banco em uso):

`/opt/importafrota/backup.sh`:

```bash
#!/bin/bash
set -euo pipefail
DATA=$(date +%Y-%m-%d)
DESTINO=/opt/importafrota/backups
mkdir -p "$DESTINO"
sqlite3 /opt/importafrota/dados/importafrota.db ".backup '$DESTINO/importafrota-$DATA.db'"
find "$DESTINO" -name "importafrota-*.db" -mtime +30 -delete
```

```bash
sudo chmod +x /opt/importafrota/backup.sh
sudo crontab -u importafrota -e
# adicionar: 0 3 * * * /opt/importafrota/backup.sh
```

Guarde os backups também fora do servidor (ex.: sincronizar `/opt/importafrota/backups`
para outro disco ou bucket), para sobreviver a uma falha total da máquina.

## 9. Deploy de uma atualização

```bash
cd /opt/importafrota/app
sudo -u importafrota git pull origin main
sudo -u importafrota .venv/bin/pip install -r requirements.txt
sudo systemctl restart importafrota
```

## 10. Verificação pós-deploy

- `curl -I https://SEU_DOMINIO/saude` deve responder `200 ok`.
- `sudo journalctl -u importafrota -f` para acompanhar logs em tempo real.
- Confirmar que `/login` só é acessível via HTTPS (o Nginx/Certbot já força o redirect).
