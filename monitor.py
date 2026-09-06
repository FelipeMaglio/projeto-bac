# -*- coding: utf-8 -*-
"""
Monitor de sinais do Telegram + simulador de martingale (cor + empate) para Bac Bo.

IMPORTANTE:
- Isto e uma SIMULACAO com saldo ficticio. Nao conecta a nenhuma casa de apostas,
  nao clica em nada e nao envia comandos para nenhum site.
- So le mensagens de um grupo do qual VOCE ja e membro, usando a sua propria conta
  do Telegram (API oficial), de forma equivalente a abrir o Telegram normalmente.

CONFIGURACAO (antes de rodar):
1. pip install telethon
2. Va em https://my.telegram.org -> "API development tools" -> crie um app.
   Voce vai receber um API_ID (numero) e um API_HASH (texto).
3. Preencha API_ID, API_HASH, CHAT_ID e SIGNAL_KEYWORD mais abaixo.
4. Rode: python monitor.py
5. Na primeira vez, o Telegram vai te pedir o numero de telefone e o codigo de
   confirmacao (chega por mensagem no proprio Telegram). Isso so acontece uma vez;
   depois fica salva uma sessao local (arquivo .session).
"""

import json
import os
import re
from datetime import datetime

from telethon import TelegramClient, events

# ========================= CONFIGURACAO =========================

API_ID = 123456                     # <-- troque pelo seu api_id (numero)
API_HASH = "SEU_API_HASH_AQUI"      # <-- troque pelo seu api_hash

# ID do chat/grupo. No link web.telegram.org/a/#-1003763969394 o ID e -1003763969394
CHAT_ID = -1003763969394

# Palavra(s) que indicam um sinal de cor. Ajuste para o que o grupo realmente usa.
SIGNAL_KEYWORDS = ["azul"]

# Pagamentos (multiplicador). Ajuste para os valores reais que voce acompanha.
PAY_COLOR = 1.0
PAY_TIE = 8.0

# Metas de lucro
PROFIT_COLOR = 100.0
PROFIT_TIE = 25.0
PROFIT_RECOVER = 75.0

SALDO_INICIAL = 1000.0
HISTORICO_ARQUIVO = "historico.json"

# ==================================================================


def carregar_estado():
    if os.path.exists(HISTORICO_ARQUIVO):
        with open(HISTORICO_ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"saldo": SALDO_INICIAL, "historico": []}


def salvar_estado(estado):
    with open(HISTORICO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def calc_step1():
    stake_color = PROFIT_COLOR / PAY_COLOR
    stake_tie = PROFIT_TIE / PAY_TIE
    return stake_color, stake_tie


def calc_recovery(perda_acumulada, ratio_tie_sobre_color):
    denom = PAY_COLOR - ratio_tie_sobre_color
    if denom <= 0:
        stake_color = PROFIT_RECOVER + perda_acumulada
    else:
        stake_color = (PROFIT_RECOVER + perda_acumulada) / denom
    stake_tie = stake_color * ratio_tie_sobre_color
    return stake_color, stake_tie


def rodar_rodada(sinal_texto, estado):
    stake_color, stake_tie = calc_step1()
    ratio = stake_tie / stake_color
    perda_acumulada = 0.0
    tentativa = 1

    while True:
        print("\n----- SINAL: {} | tentativa {}/3 -----".format(sinal_texto, tentativa))
        print("Entrada sugerida na COR:    {:.2f}".format(stake_color))
        print("Entrada sugerida no EMPATE: {:.2f}".format(stake_tie))
        if perda_acumulada > 0:
            print("(recuperando perda de {:.2f} + lucro alvo de {:.2f})".format(
                perda_acumulada, PROFIT_RECOVER))

        resultado = input("Resultado real da rodada [c=cor, e=empate, n=nao bateu]: ").strip().lower()

        if resultado == "c":
            net = (stake_color * PAY_COLOR) - stake_tie - perda_acumulada
            fechar_rodada(estado, sinal_texto, tentativa, net, "Bateu na cor")
            return
        elif resultado == "e":
            net = (stake_tie * PAY_TIE) - stake_color - perda_acumulada
            fechar_rodada(estado, sinal_texto, tentativa, net, "Bateu no empate")
            return
        elif resultado == "n":
            perda_acumulada += stake_color + stake_tie
            if tentativa >= 3:
                fechar_rodada(estado, sinal_texto, tentativa, -perda_acumulada, "Nao bateu 3x, stop")
                return
            stake_color, stake_tie = calc_recovery(perda_acumulada, ratio)
            tentativa += 1
        else:
            print("Digite 'c', 'e' ou 'n'.")


def fechar_rodada(estado, sinal_texto, tentativas, net, resultado):
    estado["saldo"] += net
    estado["historico"].append({
        "quando": datetime.now().isoformat(timespec="seconds"),
        "sinal": sinal_texto,
        "tentativas": tentativas,
        "resultado": resultado,
        "lucro_liquido": round(net, 2),
        "saldo_apos": round(estado["saldo"], 2),
    })
    salvar_estado(estado)
    sinal_str = "+" if net >= 0 else ""
    print("\n>> {} | {}{:.2f} | saldo atual: {:.2f}\n".format(resultado, sinal_str, net, estado["saldo"]))


def contem_sinal(texto):
    texto_low = texto.lower()
    return any(re.search(r"\b" + re.escape(k) + r"\b", texto_low) for k in SIGNAL_KEYWORDS)


def main():
    estado = carregar_estado()
    print("Saldo ficticio atual: {:.2f}".format(estado["saldo"]))
    print("Ouvindo o grupo {} por sinais: {}\n".format(CHAT_ID, ", ".join(SIGNAL_KEYWORDS)))

    client = TelegramClient("sessao_bacbo", API_ID, API_HASH)

    @client.on(events.NewMessage(chats=CHAT_ID))
    async def handler(event):
        texto = event.raw_text or ""
        if contem_sinal(texto):
            print("Mensagem detectada: {}".format(texto))
            rodar_rodada(texto, estado)

    client.start()
    print("Conectado. Aguardando mensagens... (Ctrl+C para sair)")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()
