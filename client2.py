from enlace import * 
import time
import sys
import datetime
from multiprocessing import Process, Queue
from datagrama import *
from timeit import default_timer as timer

serialName = "/dev/cu.usbmodem144401"               

def main():
	try:
		
		com = enlace(serialName)
	
		imageR='./img.png'
		req = input("Iniciar Comunicação? [s/n]: ")

		if req == "s":
			comecou = True
			STATE = "init"
			com.enable()
			print("Comunicação ativa, threads e comunicação serial iniciados na porta {}".format(serialName))


		log = open("Client5.txt","w")
		time.sleep(0.1)
		log.write('--------------------------------\n')
		log.write('Início de transmissão - {}\n'.format(datetime.datetime.now()))
		log.write('--------------------------------\n')
		server_id = 0 
		TIMEOUT = False
		reenvio=0

		while comecou:

			if STATE == "init":

				txBuffer0 = open(imageR,'rb').read()
				txSize0 = len(txBuffer0)

				if txSize0 % 114 == 0:
					nOfPacketsHsk = txSize0//114

				else:
					nOfPacketsHsk = txSize0//114 + 1

				header = setHead(1,0,server_id,nOfPacketsHsk,0,0,0,0,0,0)
				
				eop = (0).to_bytes(4,byteorder='big')
				pkt_new= header[0]+eop
				com.sendData(pkt_new)

				print('Tamanho do pkt enviado:', len(pkt_new))
				log.write('{} / envio / 1 / {} / 0 / {}\n'.format(datetime.datetime.now(),txSize0, nOfPacketsHsk))
				print("enviando handshake...")
				print('{} / envio / 1 / {} / 0 / {} - LOGGED'.format(datetime.datetime.now(),txSize0, nOfPacketsHsk))
				STATE = "waiting"

			if STATE == "waiting":

				print("Aguardando resposta do server...")
			
				aguardando = True

				while aguardando:

					# rxBuffer,nRx = retry(com.getData(14))
					try:
						nRx, rxBuffer = com.getData(14)
						print(nRx, rxBuffer)
					except:
						time.sleep(5)
						tryagain = input('Servidor inativo apos 5 segundos, tentar novamente?[s/n]')
						if tryagain =='s':
							STATE='waiting'
						else:
							log.write("{} / envio / 5\n".format(datetime.datetime.now()))
							log.close()
							raise Exception('conexao perdida')
						

					log.write('{} / recebimento / 2 / {}\n'.format(datetime.datetime.now(),len(rxBuffer)))
					if rxBuffer[1] == 14:
						STATE = "Connected"
						aguardando = False
						print("Servidor vivo e ativo!")
						print("STATE: {}".format(STATE))
					else:
						time.sleep(5)
						tryagain = input('Servidor inativo apos 5 segundos, tentar novamente?[s/n]')
						if tryagain == 's':
							STATE='waiting'
						else:
							STATE='Desconectado'
							log.write("{} / envio / 5\n".format(datetime.datetime.now()))
							log.close()
							raise Exception('Conexao perdida')

			if STATE == "Connected" and TIMEOUT == False:

				print("Conectando...")

				timeStart = timer()
				txBuffer = open(imageR,'rb').read()
				txSize = len(txBuffer)

				print("Tamanho txBuffer: {}".format(txSize))


				if txSize % 114 == 0:
					nOfPackets = txSize//114

				else:
					nOfPackets = txSize//114 + 1

				print("Numero de Pacotes: {}".format(nOfPackets))

				current_p = 1
				i = 0 
				p_left = nOfPackets
				pacotes_enviados = 0

				while txSize > 0 and STATE != "Desconectado":

					print("txSize maior que 0")

					if txSize >=114:

						print("fragmentando...")

						header= setHead(3,0,server_id,nOfPackets,current_p,114,current_p,current_p-1,0,0)

						print("header ok!")
						payload = txBuffer[i:i+114]
						print("payload ok!")
						eop2 = (0).to_bytes(4,byteorder='big')
						pkt_extra = header[0] + payload + eop2


						com.sendData(pkt_extra)
						log.write('{} / envio / 3 / {} / {} / 0 / {}\n'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))
						print('{} / envio / 3 / {} / {} / 0 / {} - LOGGED'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))
						

						print("pacote enviado...")


						time.sleep(0.1)
						HeaderRespostaServer, HeaderRxBuffer = com.getData(10)
						
						log.write('{} / recebimento / 4 / {}\n'.format(datetime.datetime.now(),len(HeaderRxBuffer[0])))
						print('{} / recebimento / 4 / {}\n'.format(datetime.datetime.now(),len(HeaderRxBuffer[0])))

						if HeaderRespostaServer == 0:

							# print("TIMEOUT")
							

							# log.write("{} / envio / 5\n".format(datetime.datetime.now()))
							# print(("{} / 5 - LOGGED".format(datetime.datetime.now())))

							# TIMEOUT = True
							# STATE = "Desconectado"
							# print("STATE: Desconectado")
							# comecou = False
							reenvio+=1
							if reenvio >4:
								raise Exception('Server deconectado apos 20 segundos')
							time.sleep(5)
							header= setHead(3,0,server_id,nOfPackets,current_p,114,current_p,current_p-1,0,0)

							print("header ok!")
							payload = txBuffer[i:i+114]
							print("payload ok!")
							eop2 = (0).to_bytes(4,byteorder='big')
							pkt_extra = header[0] + payload + eop2


							com.sendData(pkt_extra)
							log.write('{} / envio / 3 / {} / {} / 0 / {}\n'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))
							print('{} / envio / 3 / {} / {} / 0 / {} - LOGGED'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))
							print('Re enviando pacote anterior')
							


							

						else:	
							


							EopRespostaServer, EopRxBuffer = com.getData(4)

							log.write('{} / recebimento / 4 / {}\n'.format(datetime.datetime.now(),len(EopRxBuffer[0])))
							print('{} / recebimento / 4 / {}\n'.format(datetime.datetime.now(),len(EopRxBuffer[0])))

							if EopRxBuffer[0] == eop2:

								current_p += 1
								i += 114
								txSize -= 114
								p_left -= 1
								pacotes_enviados += 1
							else:

								print("Erro! Eop na posicao errada. Tamanho de payload incorreto")
								

							


							print("Pacote Atual: {}".format(current_p))
							print("Tamanho restante: {}".format(txSize))
							print("pacotes enviados: {}".format(pacotes_enviados))

					else:
						header = setHead(3,0,server_id,nOfPackets,current_p,txSize,current_p,current_p-1,0,0)

						payload = txBuffer[i:]
						eop2 = (0).to_bytes(4,byteorder='big')
						pkt_ex = header[0] + payload + eop2
						com.sendData(pkt_ex)
						log.write('{} / envio / 3 / {} / {} / 0 / {}\n'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))
						print('{} / envio / 3 / {} / {} / 0 / {} - LOGGED'.format(datetime.datetime.now(),txSize, current_p, nOfPackets))

						print("ultimo pacote enviado.")

						comecou = False

						STATE = "End"
						break



		if STATE == "Desconectado":

			print("Timeout...")
			log.write('--------------------------------\n')
			log.write('Fim da Transmissão as {}\n'.format(datetime.datetime.now()))
			log.write('--------------------------------\n')
			log.close()
			com.disable()
			
		if STATE == "End":

			print("Envio da imagem OK")
	
			print("-------------------------")

			rxBuffer, nRx = com.getData(1)
			print("Confirmação do recebimento da imagem OK")
			confirm = int.from_bytes(nRx[0], byteorder='big')

			if confirm == 0:
				print("FIM!")
			
			timeEnd = timer()
			delta_t = timeEnd - timeStart
			velocidadeTransferencia = txSize/delta_t

			log.write('--------------------------------\n')
			log.write('Fim da Transmissão as {}\n'.format(datetime.datetime.now()))
			log.write('--------------------------------\n')
			log.close()

			print('Taxa de transferencia: {} bytes/s' .format(velocidadeTransferencia))
			print("-------------------------")
			print("Comunicação encerrada")
			print("-------------------------")
			print("-------------------------")
			com.disable()
	except Exception as e:
		log.write('--------------------------------\n')
		log.write('Fim da Transmissão as {}\n'.format(datetime.datetime.now()))
		log.write('--------------------------------\n')
		log.close()
		com.disable()
		l,m,tb = sys.exc_info()
		print(l)
		print(e)
		print('Erro na linha:', tb.tb_lineno)


	#so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
	main()