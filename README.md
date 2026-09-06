# Monitor de sinais (simulação fictícia)

Este script roda no **seu computador** e lê as mensagens de um grupo do Telegram do qual você já é membro, usando sua própria conta. Ele não acessa nenhuma casa de apostas nem clica em nada — só calcula uma simulação com saldo fictício.

## Passo a passo

1. Instale o Python (3.9+) se ainda não tiver: https://www.python.org/downloads/
2. Abra um terminal na pasta deste arquivo e instale a biblioteca:
   ```
   pip install telethon
   ```
3. Crie um app do Telegram (grátis, leva 2 minutos):
   - Acesse https://my.telegram.org e faça login com seu número
   - Clique em "API development tools"
   - Preencha qualquer nome de app e crie
   - Copie o `api_id` (número) e o `api_hash` (texto)
4. Abra `monitor.py` e edite:
   - `API_ID` → seu api_id
   - `API_HASH` → seu api_hash
   - `CHAT_ID` → já está preenchido com `-1003763969394` (o grupo que você mandou)
   - `SIGNAL_KEYWORDS` → palavra(s) que o grupo usa para o sinal (hoje: `"azul"`)
   - `PAY_COLOR` / `PAY_TIE` → pagamentos reais da sua plataforma
5. Rode:
   ```
   python monitor.py
   ```
6. Na primeira vez, ele vai pedir seu número de telefone e o código que o Telegram te enviar por mensagem. Depois disso fica salvo (arquivo `sessao_bacbo.session`) e não pede de novo.

## Como funciona no dia a dia

- Quando alguém manda uma mensagem com a palavra do sinal (ex: "azul") no grupo, o script mostra no terminal quanto "entraria" na cor e quanto no empate.
- Você olha o resultado real da rodada e digita `c` (bateu cor), `e` (bateu empate) ou `n` (não bateu).
- Se não bater, ele recalcula e sugere a próxima entrada (até 3 tentativas), igual à calculadora visual que fiz antes.
- Tudo fica salvo em `historico.json`, incluindo o saldo fictício acumulado.

## Segurança

- Nunca compartilhe seu `api_hash` nem o arquivo `sessao_bacbo.session` — eles dão acesso à sua conta do Telegram.
- Este script não envia nem posta nada no grupo, só lê.
