from gpiozero import LED, Button, Buzzer
from time import sleep
from threading import Thread, Timer, Lock
from queue import Queue
import requests

# Endereço da API que recebe as jogadas dos botões
API_URL = "http://localhost:8000/hardware/botao"

# Tempo que o LED fica aceso ao apertar o botão
TEMPO_LED = 0.2

# Configuração dos LEDs e seus pinos no Raspberry Pi
leds = {
    "Vermelho": LED(17),
    "Amarelo": LED(23),
    "Azul": LED(22),
    "Verde": LED(27)
}

buzzer = Buzzer(24)

# Configuração dos botões e seus pinos
# pull_up=True ativa o resistor interno do botão
# bounce_time evita que um único aperto seja contado várias vezes
botoes = {
    "Vermelho": Button(19, pull_up=True, bounce_time=0.1),
    "Amarelo": Button(5, pull_up=True, bounce_time=0.1),
    "Azul": Button(6, pull_up=True, bounce_time=0.1),
    "Verde": Button(13, pull_up=True, bounce_time=0.1)
}

# Fila que guarda as jogadas antes de enviar para a API
fila_jogadas = Queue()

# Guarda os temporizadores que controlam o tempo dos LEDs
temporizadores_led = {}

# Evita conflitos ao acessar os temporizadores ao mesmo tempo
trava_led = Lock()

# Apaga o LED da cor recebida
def apagar_led(cor):
    leds[cor].off()

# Emite um som curto quando o jogador completa um nível
def som_nivel():
    buzzer.on()
    sleep(0.15)
    buzzer.off()

# Emite um som mais longo quando o jogador erra
def som_erro():
    buzzer.on()
    sleep(0.7)
    buzzer.off()

# Executada quando um botão é pressionado
def registrar_botao(cor):
    print(f"Botão pressionado: {cor}")

    # Acende o LED correspondente ao botão
    led = leds[cor]

    led.on()
    # Controla o tempo que o LED fica aceso
    with trava_led:
        if cor in temporizadores_led:
            temporizadores_led[cor].cancel()

        # Cria um temporizador para apagar o LED após 0,2 segundos
        temporizador = Timer(
            TEMPO_LED,
            apagar_led,
            args=[cor]
        )

        temporizadores_led[cor] = temporizador
        temporizador.start()

    # Adiciona a cor pressionada à fila em letras minúsculas
    fila_jogadas.put(cor.lower())

# Fica buscando as jogadas na fila e enviando para a API
def enviar_jogadas():
    while True:
        # Pega a próxima jogada da fila
        cor = fila_jogadas.get()

        try:
            # Envia a cor pressionada para o backend
            resposta = requests.post(
                API_URL,
                json={"cor": cor},
                timeout=3
            )

            # Verifica se a API recebeu a jogada corretamente
            if resposta.ok:
                dados = resposta.json()

                print(f"Jogada enviada: {cor}")

                # Verifica se o jogador concluiu o nível
                if dados.get("resultado") == "nivel_concluido":
                    print("Nível concluído!")
                    som_nivel()

                # Verifica se o jogador perdeu a partida
                elif dados.get("status") == "derrota":
                    print("Fim de jogo!")
                    som_erro()

            else:
                print("Erro na API:", resposta.text)

        except requests.RequestException as erro:
            print("Erro de conexão:", erro)

        finally:
            # Informa que a jogada foi processada
            fila_jogadas.task_done()


# Inicia o envio das jogadas em segundo plano
# Assim, o programa continua lendo os botões enquanto envia os dados
Thread(target=enviar_jogadas, daemon=True).start()

# Associa cada botão à função que será chamada quando ele for pressionado
for cor, botao in botoes.items():
    botao.when_pressed = lambda c=cor: registrar_botao(c)


print("Hardware Genius conectado!")
print("Aguardando botões...")


try:
    # Mantém o programa em execução
    while True:
        sleep(1)

except KeyboardInterrupt:
    print("\nEncerrando hardware...")

finally:
    # Cancela todos os temporizadores que ainda estiverem ativos
    with trava_led:
        for temporizador in temporizadores_led.values():
            temporizador.cancel()

    # Desliga e libera todos os LEDs
    for led in leds.values():
        led.off()
        led.close()

    # Libera os botões
    for botao in botoes.values():
        botao.close()

    # Desliga e libera o buzzer
    buzzer.off()
    buzzer.close()

    print("Hardware desligado.")
