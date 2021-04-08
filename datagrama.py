def setHead(a0,a1,a2,a3,a4,a5,a6,a7,a8,a9):
  h0 = (a0).to_bytes(1, byteorder='big')
  h1 = (a1).to_bytes(1, byteorder='big')
  h2 = (a2).to_bytes(1,byteorder='big')
  h3 = (a3).to_bytes(1,byteorder='big')
  h4 = (a4).to_bytes(1, byteorder='big')
  h5 = (a5).to_bytes(1,byteorder='big')
  h6 = (a6).to_bytes(1,byteorder='big')
  h7 = (a7).to_bytes(1,byteorder='big')
  h8 = (a8).to_bytes(1,byteorder='big')
  h9 = (a9).to_bytes(1,byteorder='big')

  header = h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9

  return [header,h3]
