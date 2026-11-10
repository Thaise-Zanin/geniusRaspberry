
from gpiozero import LED, Button, Buzzer
from time import sleep
from random import choice
from queue import Queue, Empty

# LEDs
leds = {
    "Vermelho": LED(17),
    "Amarelo": LED(23),
    "Azul": LED(22),
    "Verde": LED(27)
}

# Botoes
botoes = {
    "Vermelho": Button(19, pull_up=True),
    "Amarelo": Button(5, pull_up=True),
    "Azul": Button(6, pull_up=True),
    "Verde": Button(13, pull_up=True)
}

# Buzzer
buzzer = Buzzer(24)

# Fila de botoes
fila_botoes = Queue()

for cor, botao in botoes.items():
    botao.when_pressed = lambda c=cor: fila_botoes.put(c)


def desligar_tudo():
    for led in leds.values():
        led.off()
    buzzer.off()


def som_acerto():
    buzzer.on()
    sleep(0.2)
    buzzer.off()


def som_erro():
    buzzer.on()
    sleep(0.8)
    buzzer.off()


def esperar_jogador():
    try:
        return fila_botoes.get(timeout=8)
    except Empty:
        return None


def fim_de_jogo(pontos):
    desligar_tudo()
    print("\nGAME OVER!")
    print(f"Sua pontuacao: {pontos}")
    som_erro()


def iniciar_jogo():
    sequencia = []
    pontos = 0

    print("JOGO DA MEMORIA")
    print("Prepare-se!")

    sleep(2)

    while True:
        nova_cor = choice(list(leds.keys()))
        sequencia.append(nova_cor)

        print(f"\nRODADA {len(sequencia)}")

        # A sequencia sera mostrada pelo frontend.
        # A Raspberry nao acende LEDs nesta etapa.

        while not fila_botoes.empty():
            fila_botoes.get_nowait()

        acertou = True

        for cor_correta in sequencia:
            resposta = esperar_jogador()

            if resposta is None:
                print("Tempo esgotado!")
                acertou = False
                break

            print(f"Voce apertou: {resposta}")

            if resposta != cor_correta:
                print("Resposta incorreta!")
                acertou = False
                break

        if acertou:
            pontos += 1
            print(f"Nivel {pontos} concluido!")
            som_acerto()
            sleep(1)
        else:
            fim_de_jogo(pontos)
            break


try:
    iniciar_jogo()

except KeyboardInterrupt:
    print("\nJogo encerrado!")

finally:
    desligar_tudo()

    for led in leds.values():
        led.close()

    for botao in botoes.values():
        botao.close()

    buzzer.close()

    print("Componentes desligados.")
