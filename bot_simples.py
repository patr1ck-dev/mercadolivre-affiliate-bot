"""
BOT MERCADO LIVRE - VERSÃO FINAL OTIMIZADA
Requisições mínimas para evitar bloqueios
"""

import os
import requests
import time
from datetime import datetime

# ============================================
# CONFIGURAÇÕES
# ============================================
# Os segredos são lidos de variáveis de ambiente (veja o README),
# para que nunca sejam commitados junto com o código.

# Mercado Livre
ML_CLIENT_ID = os.environ.get("ML_CLIENT_ID", "")
ML_CLIENT_SECRET = os.environ.get("ML_CLIENT_SECRET", "")
AFFILIATE_TAG = os.environ.get("AFFILIATE_TAG", "")

# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Filtros de ofertas
MIN_DISCOUNT = 15      # Mínimo 15% de desconto
MIN_PRICE = 100        # Mínimo R$ 100
MAX_PRICE = 3000       # Máximo R$ 3000
CHECK_INTERVAL = 1800  # Verifica a cada 30 minutos (1800 segundos)

# ============================================
# CÓDIGO DO BOT
# ============================================

posted_products = set()
ml_token = None

def get_ml_token():
    """Obtém token de acesso"""
    global ml_token
    url = "https://api.mercadolibre.com/oauth/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": ML_CLIENT_ID,
        "client_secret": ML_CLIENT_SECRET
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            ml_token = response.json().get("access_token")
            return True
        return False
    except:
        return False

def search_single_term(term):
    """Busca UM termo apenas - versão minimalista"""
    deals = []
    
    headers = {
        'Authorization': f'Bearer {ml_token}' if ml_token else '',
        'User-Agent': 'MercadoLivre Affiliate Bot/1.0'
    }
    
    url = "https://api.mercadolibre.com/sites/MLB/search"
    params = {
        'q': term,
        'limit': 15,  # Apenas 15 produtos
        'sort': 'price_asc'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            
            for item in results:
                if item['id'] in posted_products:
                    continue
                
                price = item.get('price', 0)
                original_price = item.get('original_price')
                
                if original_price and original_price > price:
                    discount = ((original_price - price) / original_price) * 100
                    
                    if (discount >= MIN_DISCOUNT and 
                        MIN_PRICE <= price <= MAX_PRICE):
                        
                        deals.append({
                            'id': item['id'],
                            'title': item.get('title', '')[:60],
                            'price': price,
                            'original_price': original_price,
                            'discount': round(discount, 1),
                            'link': item.get('permalink', ''),
                            'image': item.get('thumbnail', '').replace('-I.jpg', '-O.jpg')
                        })
            
            return deals, response.status_code
            
        return [], response.status_code
        
    except:
        return [], 0

def send_telegram(deal):
    """Envia oferta para Telegram"""
    try:
        separator = '&' if '?' in deal['link'] else '?'
        link_afiliado = f"{deal['link']}{separator}aff_tag={AFFILIATE_TAG}"
        
        message = f"""🔥 SUPER OFERTA! 🔥

📦 {deal['title']}

💰 De: R$ {deal['original_price']:.2f}
💵 Por: R$ {deal['price']:.2f}
🏷️ {deal['discount']}% de desconto!

🛒 {link_afiliado}

⚡ Corre que acaba!"""
        
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'photo': deal['image'],
            'caption': message
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except:
        return False

def main():
    """Função principal - VERSÃO OTIMIZADA"""
    print("=" * 65)
    print("🤖 BOT MERCADO LIVRE - VERSÃO FINAL (Anti-Bloqueio)")
    print("=" * 65)
    print(f"⏰ Iniciado: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"\n📊 Configurações:")
    print(f"   • Desconto mínimo: {MIN_DISCOUNT}%")
    print(f"   • Faixa de preço: R$ {MIN_PRICE} - R$ {MAX_PRICE}")
    print(f"   • Intervalo de verificação: {CHECK_INTERVAL//60} minutos")
    print("=" * 65)
    
    # Testa Telegram
    print("\n📱 Testando Telegram...")
    try:
        r = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe", timeout=10)
        if r.status_code == 200:
            bot_name = r.json()['result']['username']
            print(f"   ✅ Conectado! Bot: @{bot_name}")
        else:
            print(f"   ❌ Erro na conexão com Telegram")
            return
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return
    
    # Tenta autenticar (opcional)
    print("\n🔐 Tentando autenticação ML...")
    if get_ml_token():
        print("   ✅ Token obtido!")
    else:
        print("   ⚠️ Sem token (vamos tentar sem autenticação)")
    
    print("\n" + "=" * 65)
    print("🚀 BOT INICIADO - Buscando ofertas...\n")
    print("💡 DICA: Deixe o bot rodando. Ele vai verificar a cada 30 min.")
    print("   Para parar, aperte Ctrl+C")
    print("=" * 65)
    
    # Lista rotativa de termos (busca 1 por vez)
    search_terms = [
        'smartphone samsung',
        'notebook',
        'smart tv',
        'airpods',
        'playstation 5'
    ]
    
    current_term_index = 0
    iteration = 1
    blocked_count = 0
    
    while True:
        try:
            print(f"\n{'─'*65}")
            print(f"🔄 Verificação #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
            print(f"{'─'*65}")
            
            # Busca apenas 1 termo por verificação
            term = search_terms[current_term_index]
            print(f"🔍 Buscando: '{term}'...")
            
            deals, status_code = search_single_term(term)
            
            # Verifica se foi bloqueado
            if status_code == 403:
                blocked_count += 1
                print(f"   ⚠️ BLOQUEADO (403)")
                
                if blocked_count >= 3:
                    print(f"\n{'='*65}")
                    print("🛑 BLOQUEIO DETECTADO")
                    print("=" * 65)
                    print("⚠️ Você está bloqueado pelo Mercado Livre.")
                    print("\n📋 O que fazer:")
                    print("   1. Pare o bot (Ctrl+C)")
                    print("   2. Aguarde 2-3 horas")
                    print("   3. Execute novamente")
                    print("\n💡 OU tente de outra rede (WiFi diferente/4G)")
                    print("=" * 65)
                    time.sleep(60)
                    blocked_count = 0
                else:
                    print(f"   ⏰ Aguardando mais tempo...")
                    time.sleep(300)  # 5 minutos
                
            elif status_code == 200:
                blocked_count = 0  # Reset contador
                print(f"   ✅ Busca OK! {len(deals)} ofertas válidas")
                
                if len(deals) > 0:
                    print(f"\n   📤 Enviando ofertas...")
                    
                    for i, deal in enumerate(deals, 1):
                        print(f"      [{i}] {deal['title']}")
                        print(f"          💰 R$ {deal['price']:.2f} ({deal['discount']}% OFF)")
                        
                        if send_telegram(deal):
                            print(f"          ✅ Enviado!")
                            posted_products.add(deal['id'])
                        else:
                            print(f"          ❌ Falha no envio")
                        
                        time.sleep(5)  # 5 segundos entre posts
                    
                    print(f"\n   ✨ {len(deals)} ofertas postadas!")
                else:
                    print(f"   💭 Nenhuma oferta com {MIN_DISCOUNT}%+ de desconto")
            
            else:
                print(f"   ⚠️ Status {status_code}")
            
            # Rotaciona para próximo termo
            current_term_index = (current_term_index + 1) % len(search_terms)
            
            print(f"\n⏳ Próxima verificação em {CHECK_INTERVAL//60} minutos...")
            print(f"   ({iteration} buscas | {len(posted_products)} produtos postados)")
            
            iteration += 1
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print(f"\n\n{'='*65}")
            print("👋 BOT ENCERRADO")
            print("=" * 65)
            print(f"📊 Estatísticas finais:")
            print(f"   • Buscas realizadas: {iteration - 1}")
            print(f"   • Produtos postados: {len(posted_products)}")
            print(f"   • Tempo de execução: {((iteration-1) * CHECK_INTERVAL)//60} minutos")
            print("=" * 65)
            break
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("   Aguardando 2 minutos...")
            time.sleep(120)

if __name__ == "__main__":
    main()