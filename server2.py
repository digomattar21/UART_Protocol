
import time
import sys
from enlace import *
import datetime
from datagrama import *

serialName = "/dev/cu.usbmodem144101"                  


def main():
	try:
   
		com = enlace(serialName)
		com.enable()
	
		print("Comunicação ativa, threads e comunicação serial iniciados {}".format(serialName))
		
		listening = True
		STATE = "init"
		imageW = "./received.png" 
		img = bytes(0)
		server_id = 1
		log = open('Server5.txt','w')
		log.write('--------------------------------\n')
		log.write('Início de transmissão - {}\n'.format(datetime.datetime.now()))
		log.write('--------------------------------\n')
		TIMEOUT = False

		while listening:
			if STATE == "init":
				hsk = True
				while hsk:
					
					rxBuffer, nRx = com.getData(14)
					buffer=nRx[0]
					
					log.write('{} / recebimento / 1 /{}\n'.format(datetime.datetime.now(),nRx[1]))
					print('{} / recebimento / 1 /{}\n'.format(datetime.datetime.now(),nRx[1]))

					time.sleep(0.1)
					print('recebeu {} bytes de dados' .format(nRx[1]))


					if nRx[0][0] == 1 and nRx[0][2] == 0:

						print("Verificação do header feita")

						header = setHead(2,0,server_id,buffer[3],0,0,0,0,0,0)
						
						eop = (0).to_bytes(4,byteorder='big')
						pkt = header[0] + eop
						com.sendData(pkt)
						time.sleep(0.5)
						print("Handshake Enviado")
						log.write('{} / envio / 2 / 0 / {}\n'.format(datetime.datetime.now(),int.from_bytes(header[1],byteorder='big')))
						print('{} / envio / 2 / 0 / {}\n'.format(datetime.datetime.now(),int.from_bytes(header[1],byteorder='big')))
						STATE = "Alive"
						print("STATE {}".format(STATE))
						hsk = False

					else: 
						print("Verificação do header falhou")

			if TIMEOUT == False and  STATE == "Alive":
				rxBuffer, nRx = com.getData(10)
				buffer = nRx[0]
				print(rxBuffer, nRx)

				print('Mensagem recebida')

				if rxBuffer == 0:
					print('TIMEOUT')
					header = setHead(5,0,0,0,0,0,0,0,0,0)

					log.write("{} / envio / 5\n".format(datetime.datetime.now()))
					print(("{} / 5 - LOGGED".format(datetime.datetime.now())))
					print("TIMEOUT")
					TIMEOUT = True
					STATE = "Conexão Perdida"
					print("STATE: Conexão Perdida")
					listening = False
				else:
					tipo_de_mensagem = buffer[0]
					idClient = buffer[2]
					nOfPackets = buffer[3]
					currentPacket = buffer[4]
					tamanho = buffer[5]
					leftOfPacket = buffer[6]
					ultimoPacket = buffer[7]
					cr1 = buffer[8]
					cr2 = buffer[9]

					print("Pacote Atual: {}".format(currentPacket))
					print("Tamanho: {}".format(tamanho))

					txBuffer, nTx = com.getData(tamanho)

					img += nTx[0]

					print("Tamanho do Payload: {}".format(len(nTx[0])))

					eop, nEop = com.getData(4)
					eopP = nEop[0]

					log.write('{} / recebimento / 3 / {} / {} / 0 / {}\n'.format(datetime.datetime.now(),tamanho, currentPacket, nOfPackets))

					header = setHead(4,0,server_id,nOfPackets,currentPacket,tamanho,leftOfPacket,ultimoPacket,cr1,cr2)

					payload = 0
				
					pkt = header[0] + eopP

					print(currentPacket, ultimoPacket)
					if currentPacket == (ultimoPacket+1):
						ultimoPacket +=1
						com.sendData(pkt)
						log.write('{} / envio / 4 / 14\n'.format(datetime.datetime.now()))
						print('{} / envio / 4 / 14\n - LOGGED'.format(datetime.datetime.now()))
					else:
						print("Ordem de recebimento incorreta")
						header = setHead(6,0,server_id,nOfPackets,currentPacket,tamanho,leftOfPacket,ultimoPacket,cr1,cr2)
									
						pkt = header[0] + eopP
						com.sendData(pkt)
						log.write("'{} / envio / 6 / {}".format(datetime.datetime.now(), leftOfPacket))
						

					if tamanho < 114:

						com.disable()
						print("Último pacote recebido")
						break

		if STATE == "Conexão Perdida":

			print("Timeout...")
			log.write('--------------------------------\n')
			log.write('Fim da Transmissão as {}\n'.format(datetime.datetime.now()))
			log.write('--------------------------------\n')
			log.close()
			com.disable()

		print ("Início da população dos dados na imagem:" + ' - ' + imageW)
		f = open(imageW, 'wb')
		f.write(img)
		print("Fim da população da imagem!")

		com.sendData((0).to_bytes(1, byteorder='big'))
		print("Confirmação de escritura enviada")
		print("----------------------")
		print("Comunicação encerrada")
		print("----------------------")
		print("----------------------")
		
	except Exception as e:
		log.write('--------------------------------\n')
		log.write('Fim da Transmissão as {}'.format(datetime.datetime.now()))
		log.write('--------------------------------\n')
		log.close()
		com.disable()
		l,m,tb = sys.exc_info()
		print(l)
		print(e)
		print('Erro na linha:', tb.tb_lineno)

if __name__ == "__main__":
	main()
