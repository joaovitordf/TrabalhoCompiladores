from os import path

class TipoToken:
    ID = (1, 'id')
    DOISPTOS = (2, ':')
    ATRIB = (3, '=')
    VIRG = (4, ',')
    PTOVIRG = (5, ';')
    ADD = (6, '+')
    SUBT = (7, '-')
    DIV = (8, '/')
    MULT = (9, '*')
    OR = (10, '||')
    AND = (11, '&&')
    COMPARA = (12, '==')
    MAIORIGUAL = (13, '>=')
    MENORIGUAL = (14, '<=')
    DIFERENTE = (15, '!=')
    MAIOR = (16, '>')
    MENOR = (17, '<')
    NEGAR = (18, '!')
    ABREP = (19, '(')
    FECHAP = (20, ')')
    PRINT = (21, '@')
    PTO = (22, '.')
    IF = (23, 'if')
    ELSE = (24, 'else')
    VAR = (25, 'var')
    FUNCTION = (26, 'function')
    RETURN = (27, 'return')
    WHILE = (28, 'while')
    FIMARQ = (29, 'fim-de-arquivo')
    ABRLIST = (30, '[')
    FCHLIST = (31, ']')
    ERROR = (32, 'erro')
    NUMINT = (33, 'numero-int')
    NUMFLOAT = (34, 'numero-float')
    ABRCHV = (35, '{')
    FCHCHV = (36, '}')
    MODULO = (37, '%')

class Token:
    def __init__(self, tipo, lexema, linha):
        self.tipo = tipo
        (const, msg) = tipo
        self.const = const
        self.msg = msg
        self.lexema = lexema
        self.linha = linha

class Lexico:
    # dicionario de palavras reservadas
    reservadas = {
        'IF': TipoToken.IF,
        'ELSE': TipoToken.ELSE,
        '@': TipoToken.PRINT,
        'VAR': TipoToken.VAR,
        'FUNCTION': TipoToken.FUNCTION, 
        'RETURN': TipoToken.RETURN,
        'WHILE': TipoToken.WHILE
    }
    
    hexadecimal = { 'a', 'b', 'c', 'd', 'e', 'f', 'A', 'B', 'C', 'D', 'E', 'F'}

    def __init__(self, nomeArquivo):
        self.nomeArquivo = nomeArquivo
        self.arquivo = None
        # os atributos buffer e linha sao incluidos no metodo abreArquivo

    def abreArquivo(self):
        if not self.arquivo is None:
            print('ERRO: Arquivo ja aberto')
            quit()
        elif path.exists(self.nomeArquivo):
            self.arquivo = open(self.nomeArquivo, "r")
            # fila de caracteres 'deslidos' pelo ungetChar
            self.buffer = ''
            self.linha = 1
        else:
            print('ERRO: Arquivo "%s" inexistente.' % self.nomeArquivo)
            quit()

    def fechaArquivo(self):
        if self.arquivo is None:
            print('ERRO: Nao ha arquivo aberto')
            quit()
        else:
            self.arquivo.close()

    def getChar(self):
        if self.arquivo is None:
            print('ERRO: Nao ha arquivo aberto')
            quit()
        elif len(self.buffer) > 0:
            c = self.buffer[0]
            self.buffer = self.buffer[1:]
            return c
        else:
            c = self.arquivo.read(1)
            # se nao foi eof, pelo menos um car foi lido
            # senao len(c) == 0
            if len(c) == 0:
                return None
            else:
                return c

    def ungetChar(self, c):
        if not c is None:
            self.buffer = self.buffer + c

    def getToken(self):
        lexema = ''
        estado = 1
        car = None
        while (True):
            if estado == 1:
                # estado inicial que faz primeira classificacao
                car = self.getChar()
                if car is None:
                    return Token(TipoToken.FIMARQ, '<eof>', self.linha)
                elif car in {' ', '\t', '\n'}:
                    if car == '\n':
                        self.linha = self.linha + 1
                # Caracter esta no alfabeto
                elif car.isalpha():
                    estado = 2
                # Caracter eh um numero
                elif car.isdigit():
                    estado = 3
                # Simbolos de soma, atribuicao, etc
                elif car in {':', '=', ',', ';', '+', '-', '/', '*', '|', '&', '>', '<', '!', '(', ')', '@', '.', '[', ']', '{', '}', '%'}:
                    estado = 4
                # Comentario
                elif car == '#':
                    estado = 5
                else:
                    return Token(TipoToken.ERROR, '<' + car + '>', self.linha)
            # Caracter esta no alfabeto
            elif estado == 2:
                # estado que trata nomes (identificadores ou palavras reservadas)
                lexema = lexema + car
                car = self.getChar()
                if car is None or (not car.isalnum()):
                    # terminou o nome
                    self.ungetChar(car)
                    # Identificadores validos tem o maximo 32 caracteres
                    if len(lexema) > 32:
                        return Token(TipoToken.ERROR, lexema, self.linha)
                    if lexema in Lexico.reservadas:
                        return Token(Lexico.reservadas[lexema], lexema, self.linha)
                    else:
                        return Token(TipoToken.ID, lexema, self.linha)
            # Caracter eh um numero
            elif estado == 3:
                lexema = lexema + car
                car = self.getChar()
                if lexema == '0':
                    if car == 'x' or car == 'X':
                        # estado que trata numeros hexadecimais
                        estado = 7
                    elif car != '.':
                        if car is None or (not car.isdigit()):
                            # terminou o numero
                            self.ungetChar(car)
                            return Token(TipoToken.NUMINT, lexema, self.linha)
                    else:
                        lexema = lexema + car
                        estado = 6
                else:
                    if car != '.':
                        if car is None or (not car.isdigit()):
                            # terminou o numero
                            self.ungetChar(car)
                            return Token(TipoToken.NUMINT, lexema, self.linha)
                    else:
                        # estado que trata numeros decimais
                        lexema = lexema + car
                        estado = 6
            elif estado == 4:
                # estado que trata outros tokens primitivos comuns
                lexema = lexema + car
                if car == ':':
                    return Token(TipoToken.DOISPTOS, lexema, self.linha)
                # Caso seja lido um caracter =, eh possivel que venha outro
                # caracter =, fazendo com que seja utilizado a operacao
                # de comparacao(==) e nao atribuicao(=)
                elif car == '=':
                    # le o proximo caracter do buffer
                    aux = self.getChar()
                    # se o caracter for =
                    # o token sera ==
                    if aux == '=':
                        lexema = lexema + aux
                    if lexema == '==':
                        return Token(TipoToken.COMPARA, lexema, self.linha)
                    else:
                        # se o carater nao for =
                        # retira o caracter lido do buffer
                        self.ungetChar(aux)
                        return Token(TipoToken.ATRIB, lexema, self.linha)
                elif car == ',':
                    return Token(TipoToken.VIRG, lexema, self.linha)
                elif car == ';':
                    return Token(TipoToken.PTOVIRG, lexema, self.linha)
                elif car == '+':
                    return Token(TipoToken.ADD, lexema, self.linha)
                elif car == '-':
                    return Token(TipoToken.SUBT, lexema, self.linha)
                elif car == '/':
                    return Token(TipoToken.DIV, lexema, self.linha)
                elif car == '*':
                    return Token(TipoToken.MULT, lexema, self.linha)
                elif car == '|':
                    if aux == '|':
                        lexema = lexema + aux
                    if lexema == '||':
                        return Token(TipoToken.OR, lexema, self.linha)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.ERROR, lexema, self.linha)
                elif car == '&':
                    aux = self.getChar()
                    if aux == '&':
                        lexema = lexema + aux
                    if lexema == '&&':
                        return Token(TipoToken.AND, lexema, self.linha)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.ERROR, lexema, self.linha)
                elif car == '>':
                    aux = self.getChar()
                    if aux == '=':
                        lexema = lexema + aux
                    if lexema == '>=':
                        return Token(TipoToken.MAIORIGUAL, lexema, self.linha)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.MAIOR, lexema, self.linha)
                elif car == '<':
                    aux = self.getChar()
                    if aux == '=':
                        lexema = lexema + aux
                    if lexema == '<=':
                        return Token(TipoToken.MENORIGUAL, lexema, self.linha)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.MENOR, lexema, self.linha)
                elif car == '!':
                    aux = self.getChar()
                    if aux == '=':
                        lexema = lexema + aux
                    if lexema == '!=':
                        return Token(TipoToken.DIFERENTE, lexema, self.linha)
                    else:
                        self.ungetChar(aux)
                        return Token(TipoToken.NEGAR, lexema, self.linha)
                elif car == '(':
                    return Token(TipoToken.ABREP, lexema, self.linha)
                elif car == ')':
                    return Token(TipoToken.FECHAP, lexema, self.linha)
                elif car == '@':
                    return Token(TipoToken.PRINT, lexema, self.linha)
                elif car == '.':
                    return Token(TipoToken.PTO, lexema, self.linha)
                elif car == '[':
                    return Token(TipoToken.ABRLIST, lexema, self.linha)
                elif car == ']':
                    return Token(TipoToken.FCHLIST, lexema, self.linha)
                elif car == '{':
                    return Token(TipoToken.ABRCHV, lexema, self.linha)
                elif car == '}':
                    return Token(TipoToken.FCHCHV, lexema, self.linha)
                elif car == '%':
                    return Token(TipoToken.MODULO, lexema, self.linha)
            elif estado == 5:
                # consumindo comentario
                while (not car is None) and (car != '\n'):
                    car = self.getChar()
                self.ungetChar(car)
                estado = 1
            # Numero decimal
            elif estado == 6:
                if car.isdigit():
                    lexema = lexema + car
                car = self.getChar()
                if car is None or (not car.isdigit()):
                    # terminou o numero
                    self.ungetChar(car)
                    return Token(TipoToken.NUMFLOAT, lexema, self.linha)
            # Hexadecimal
            elif estado == 7:
                lexema = lexema + car
                car = self.getChar()
                if (car not in Lexico.hexadecimal):
                    if car is None or (not car.isdigit()):
                        # terminou o numero
                        self.ungetChar(car)
                        # Converte hexadecimal em int
                        lexema = int(lexema, 16)
                        return Token(TipoToken.NUMINT, lexema, self.linha)


if __name__== "__main__":

   #nome = input("Entre com o nome do arquivo: ")
   nome = 'exemplo.toy'
   lex = Lexico(nome)
   lex.abreArquivo()

   while(True):
       token = lex.getToken()
       print("token= %s , lexema= (%s), linha= %d" % (token.msg, token.lexema, token.linha))
       if token.const == TipoToken.FIMARQ[0]:
           break
   lex.fechaArquivo()
