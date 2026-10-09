# 🛒 Bot de Ofertas do Mercado Livre

Bot em Python que monitora ofertas no Mercado Livre, filtra por desconto e faixa de preço e publica as melhores num chat/canal do Telegram, com o link de afiliado.

## Como funciona

1. A cada **30 minutos** o bot busca **um termo** da lista (smartphone, notebook, smart TV, AirPods, PlayStation 5), em rodízio. Isso mantém o número de requisições baixo.
2. Entre os resultados, mantém só produtos com **desconto mínimo de 15%** e preço entre **R$ 100 e R$ 3.000** (valores ajustáveis no topo de `bot_simples.py`).
3. Posta cada oferta no Telegram com foto, preço original, preço atual, percentual de desconto e o link com a tag de afiliado.
4. Guarda os IDs já publicados para não repetir a mesma oferta durante a execução.

## Limitações conhecidas

- A API de busca do Mercado Livre pode responder **403 (bloqueio)**. O bot espera e avisa no terminal; se persistir, aguarde algumas horas ou troque de rede.
- A lista de produtos já publicados fica só em memória e é zerada quando o bot reinicia.

## Tecnologias

Python · `requests` · Mercado Livre API · Telegram Bot API

## Como rodar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure as variáveis de ambiente (use `.env.exemplo` como referência):
   ```bash
   export ML_CLIENT_ID=...
   export ML_CLIENT_SECRET=...
   export AFFILIATE_TAG=...
   export TELEGRAM_BOT_TOKEN=...
   export TELEGRAM_CHAT_ID=...
   ```
3. Inicie o bot:
   ```bash
   python bot_simples.py
   ```
   Para parar, use `Ctrl+C`.

## ⚠️ Segurança

Nunca coloque tokens ou chaves direto no código nem envie o arquivo `.env` ao repositório (ele já está no `.gitignore`).
