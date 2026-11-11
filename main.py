from gpiozero import LED, Button, Buzzer
from time import sleep
from threading import Thread, Timer, Lock
from queue import Queue
import requests

API_URL = "http://localhost:8000/hardware/botao"
TEMPO_LED = 0.2

leds = {
    "Vermelho": LED(17),
    "Amarelo": LED(23),
    "Azul": LED(22),
    "Verde": LED(27)
}

buzzer = Buzzer(24)

botoes = {
    "Vermelho": Button(19, pull_up=True, bounce_time=0.1),
    "Amarelo": Button(5, pull_up=True, bounce_time=0.1),
    "Azul": Button(6, pull_up=True, bounce_time=0.1),
    "Verde": Button(13, pull_up=True, bounce_time=0.1)
}

fila_jogadas = Queue()
temporizadores_led = {}
trava_led = Lock()


def apagar_led(cor):
    leds[cor].off()


def som_nivel():
    buzzer.on()
    sleep(0.15)
    buzzer.off()


def som_erro():
    buzzer.on()
    sleep(0.7)
    buzzer.off()


def registrar_botao(cor):
    print(f"Botão pressionado: {cor}")

    led = leds[cor]

    led.on()

    with trava_led:
        if cor in temporizadores_led:
            temporizadores_led[cor].cancel()

        temporizador = Timer(
            TEMPO_LED,
            apagar_led,
            args=[cor]
        )

        temporizadores_led[cor] = temporizador
        temporizador.start()

    fila_jogadas.put(cor.lower())


def enviar_jogadas():
    while True:
        cor = fila_jogadas.get()

        try:
            resposta = requests.post(
                API_URL,
                json={"cor": cor},
                timeout=3
            )

            if resposta.ok:
                dados = resposta.json()

                print(f"Jogada enviada: {cor}")

                if dados.get("resultado") == "nivel_concluido":
                    print("Nível concluído!")
                    som_nivel()

                elif dados.get("status") == "derrota":
                    print("Fim de jogo!")
                    som_erro()

            else:
                print("Erro na API:", resposta.text)

        except requests.RequestException as erro:
            print("Erro de conexão:", erro)

        finally:
            fila_jogadas.task_done()


Thread(target=enviar_jogadas, daemon=True).start()


for cor, botao in botoes.items():
    botao.when_pressed = lambda c=cor: registrar_botao(c)


print("Hardware Genius conectado!")
print("Aguardando botões...")


try:
    while True:
        sleep(1)

except KeyboardInterrupt:
    print("\nEncerrando hardware...")

finally:
    with trava_led:
        for temporizador in temporizadores_led.values():
            temporizador.cancel()

    for led in leds.values():
        led.off()
        led.close()

    for botao in botoes.values():
        botao.close()

    buzzer.off()
    buzzer.close()

    print("Hardware desligado.")
