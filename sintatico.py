from lexico import TipoToken as tt, Token, Lexico
from tabela import TabelaSimbolos
from semantico import Semantico

class Sintatico:

    def __init__(self):
        self.lex = None
        self.tokenAtual = None
        self.deuErro = False
        self.modoPanico = False
        self.tokensDeSincronismo = [tt.PTOVIRG, tt.FIMARQ]

    def traduz(self, nomeArquivo):
        if not self.lex is None:
            print('ERRO: Já existe um arquivo sendo processado.')
        else:
            self.deuErro = False
            self.lex = Lexico(nomeArquivo)
            self.lex.abreArquivo()
            self.tokenAtual = self.lex.getToken()

            # inicio reconhecimento do fonte
            self.tabsimb = TabelaSimbolos()
            self.semantico = Semantico()
            while True:
                if not self.tokenEsperadoEncontrado(tt.FIMARQ):
                    self.program()
                else:
                    self.consome(tt.FIMARQ)
                    break
            # fim do reconhecimento do fonte
            
            self.lex.fechaArquivo()
            return not self.deuErro

    def tabelaSimbolos(self):
        return self.tabsimb.tabelaValores()

    def tokenEsperadoEncontrado(self, token):
        (const, msg) = token
        if self.tokenAtual.const == const:
            return True
        else:
            return False

    def consome(self, token):
        if not self.modoPanico and self.tokenEsperadoEncontrado(token):
            # tudo seguindo de acordo
            self.tokenAtual = self.lex.getToken()
        elif not self.modoPanico:
            # agora deu erro, solta msg e entra no modo panico
            self.modoPanico = True
            self.deuErro = True
            (const, msg) = token
            print('ERRO DE SINTAXE [linha %d]: era esperado "%s" mas veio "%s"'
                  % (self.tokenAtual.linha, msg, self.tokenAtual.lexema))
            # quit()
            procuraTokenDeSincronismo = True
            while procuraTokenDeSincronismo:
                self.tokenAtual = self.lex.getToken()
                for tk in self.tokensDeSincronismo:
                    (const, msg) = tk
                    if self.tokenAtual.const == const:
                        # tokenAtual eh um token de sincronismo
                        procuraTokenDeSincronismo = False
                        break
        elif self.tokenEsperadoEncontrado(token):
            # chegou no ponto de sincronismo :)
            self.tokenAtual = self.lex.getToken()
            self.modoPanico = False
        else:
            # so continua, consumindo e consumindo...
            pass

    def salvaLexema(self):
        return self.tokenAtual.lexema

    def salvaLinha(self):
        return self.tokenAtual.linha

    # Verifica o retorno de um comando IF ou WHILE
    # se o retorno for 0(false), a condicao if ou while eh ignorada
    # se for 1(true), entra na condicao if ou while
    def testaRetornoCondicional(self, var):
        if var == 0:
            return False
        else:
            return True

    ##################################################################
    # Segue uma funcao para cada variavel da gramatica
    ##################################################################

    def program(self):
        self.definition()

    def definition(self):
        if self.tokenEsperadoEncontrado(tt.VAR):
            self.def_variable()
        elif self.tokenEsperadoEncontrado(tt.FUNCTION):
            self.def_function()

    def def_variable(self):
        self.consome(tt.VAR)
        lexema = self.tokenAtual.lexema
        self.consome(tt.ID)
        self.consome(tt.DOISPTOS)
        valor = self.tokenAtual.lexema
        self.type()
        if not self.tabsimb.existeIdent(lexema):
            self.tabsimb.declaraIdent(lexema, valor)
        else:
            self.tabsimb.atribuiValor(lexema, valor)
        self.consome(tt.PTOVIRG)

    def type(self):
        self.consome(tt.ID)

    def def_function(self):
        self.consome(tt.FUNCTION)
        self.consome(tt.ID)
        self.consome(tt.ABREP)
        self.parameters()
        self.consome(tt.FECHAP)
        if self.tokenEsperadoEncontrado(tt.DOISPTOS):
            self.consome(tt.DOISPTOS)
            self.type()
        self.block()

    def parameters(self):
        # O if  seria devido a especificacao da linguagem
        # onde [parameter] significa que existe ou nao a funcao
        # caso tenha um id, a funcao sera executada
        if self.tokenEsperadoEncontrado(tt.ID):
            self.parameter()
            # O while True seria devido a especificacao da linguagem
            # onde {parameter} significa que a funcao eh executada
            # zero ou mais vezes
            while True:
                if self.tokenEsperadoEncontrado(tt.VIRG):
                    self.consome(tt.VIRG)
                    self.parameter()
                else:
                    break

    def parameter(self):
        self.consome(tt.ID)
        self.consome(tt.DOISPTOS)
        self.type()

    def block(self):
        self.consome(tt.ABRCHV)
        while True:
            # def_variable sempre comeca com VAR
            if self.tokenEsperadoEncontrado(tt.VAR):
                self.def_variable()
            else:
                break
        # statement sempre comeca com um dos seguintes tokens:
        while True:
            if (self.tokenEsperadoEncontrado(tt.IF) or
                self.tokenEsperadoEncontrado(tt.WHILE) or
                self.tokenEsperadoEncontrado(tt.ID) or
                self.tokenEsperadoEncontrado(tt.NEGAR) or
                self.tokenEsperadoEncontrado(tt.ADD) or
                self.tokenEsperadoEncontrado(tt.SUBT) or
                self.tokenEsperadoEncontrado(tt.NUMINT) or
                self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
                self.tokenEsperadoEncontrado(tt.ABREP) or
                self.tokenEsperadoEncontrado(tt.RETURN) or
                self.tokenEsperadoEncontrado(tt.PRINT) or
                    self.tokenEsperadoEncontrado(tt.ABRCHV)):
                self.statement()
            else:
                break

        self.consome(tt.FCHCHV)

    def statement(self):
        if self.tokenEsperadoEncontrado(tt.IF):
            self.consome(tt.IF)
            self.exp()
            self.block()
            if self.tokenEsperadoEncontrado(tt.ELSE):
                self.consome(tt.ELSE)
                self.block()
        elif self.tokenEsperadoEncontrado(tt.WHILE):
            self.consome(tt.WHILE)
            self.exp()
            self.block()
        elif self.tokenEsperadoEncontrado(tt.RETURN):
            self.consome(tt.RETURN)
            if (self.tokenEsperadoEncontrado(tt.NEGAR) or
                self.tokenEsperadoEncontrado(tt.ADD) or
                self.tokenEsperadoEncontrado(tt.SUBT) or
                self.tokenEsperadoEncontrado(tt.NUMINT) or
                self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
                    self.tokenEsperadoEncontrado(tt.ABREP)):
                self.exp()
            self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.ID):
            # Armazena o ID em uma variavel secundaria para que
            # seja possivel visualizar o proximo token, assim
            # eh possivel saber qual caminho seguir
            token = tt.ID
            lexema = self.salvaLexema()
            self.consome(tt.ID)
            if self.tokenEsperadoEncontrado(tt.ABREP):
                self.call()
                self.consome(tt.PTOVIRG)
            elif self.tokenEsperadoEncontrado(tt.ATRIB):
                self.var(token, lexema)
            # Vale ressaltar que a adicao do ABRLIST se deve ao fato
            # de que anteriormente nao era possivel alcancar o
            # indice de um vetor, o que faria uma funcao do semantico
            # nao funcionar, logo, foi adicionado este token
            elif self.tokenEsperadoEncontrado(tt.ABRLIST):
                self.varaux()
        elif (self.tokenEsperadoEncontrado(tt.NEGAR) or
                self.tokenEsperadoEncontrado(tt.ADD) or
                self.tokenEsperadoEncontrado(tt.SUBT) or
                self.tokenEsperadoEncontrado(tt.NUMINT) or
                self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
                self.tokenEsperadoEncontrado(tt.ABREP)):
            self.exp()
            self.varaux()
        elif self.tokenEsperadoEncontrado(tt.PRINT):
            self.consome(tt.PRINT)
            self.exp()
            self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.ABRCHV):
            self.block()

    def var(self, token, lexema):
        if token == tt.ID:
            self.consome(tt.ATRIB)
            valor = self.exp()
            self.consome(tt.PTOVIRG)
            self.semantico.testaVarNaoDeclarada(lexema, self.tokenAtual.linha, self.tabsimb)
            if not self.tabsimb.existeIdent(lexema):
                self.tabsimb.declaraIdent(lexema, valor)
            else:
                self.tabsimb.atribuiValor(lexema, valor)
        elif (self.tokenEsperadoEncontrado(tt.NEGAR) or
              self.tokenEsperadoEncontrado(tt.ADD) or
              self.tokenEsperadoEncontrado(tt.SUBT) or
              self.tokenEsperadoEncontrado(tt.NUMINT) or
              self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
              self.tokenEsperadoEncontrado(tt.ABREP) or
              self.tokenEsperadoEncontrado(tt.ABRLIST)):
            self.exp()
            self.varaux()

    def varaux(self):
        if self.tokenEsperadoEncontrado(tt.ABRLIST):
            self.consome(tt.ABRLIST)
            valor = self.exp()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            self.consome(tt.FCHLIST)
            if self.tokenEsperadoEncontrado(tt.ATRIB):
                self.consome(tt.ATRIB)
                self.exp()
                self.consome(tt.PTOVIRG)
        elif self.tokenEsperadoEncontrado(tt.PTO):
            self.consome(tt.PTO)
            self.consome(tt.ID)
            if self.tokenEsperadoEncontrado(tt.ATRIB):
                self.consome(tt.ATRIB)
                self.exp()
                self.consome(tt.PTOVIRG)

    def exp(self):
        valor = self.atrib()
        return valor

    def atrib(self):
        valor = self.orfunc()
        self.restoAtrib()
        return valor

    def restoAtrib(self):
        if self.tokenEsperadoEncontrado(tt.ATRIB):
            self.consome(tt.ATRIB)
            self.atrib()
        else:
            pass

    def orfunc(self):
        valor = self.andfunc()
        self.restoOr()
        return valor

    def restoOr(self):
        if self.tokenEsperadoEncontrado(tt.OR):
            self.consome(tt.OR)
            self.andfunc()
            self.restoOr()
        else:
            pass

    def andfunc(self):
        valor = self.notfunc()
        self.restoAnd()
        return valor

    def restoAnd(self):
        if self.tokenEsperadoEncontrado(tt.AND):
            self.consome(tt.AND)
            self.notfunc()
            self.restoAnd()
        else:
            pass

    def notfunc(self):
        if self.tokenEsperadoEncontrado(tt.NEGAR):
            self.consome(tt.NEGAR)
            self.notfunc()
        elif (self.tokenEsperadoEncontrado(tt.ADD) or
              self.tokenEsperadoEncontrado(tt.SUBT) or
              self.tokenEsperadoEncontrado(tt.NUMINT) or
              self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
              self.tokenEsperadoEncontrado(tt.ABREP)):
            valor = self.rel()
            return valor

    def rel(self):
        valor1 = self.addfunc()
        tokenLogico = self.tokenAtual.lexema
        valor2 = self.restoRel()
        if valor2 != None:
            self.semantico.testaTipoInteiro(valor1, self.tokenAtual.linha)
        if tokenLogico == '==':
            if valor1 == valor2:
                return 1
            else:
                return 0
        elif tokenLogico == '!=':
            if valor1 != valor2:
                return 1
            else:
                return 0
        elif tokenLogico == '<':
            if valor1 < valor2:
                return 1
            else:
                return 0
        elif tokenLogico == '<=':
            if valor1 <= valor2:
                return 1
            else:
                return 0
        elif tokenLogico == '>':
            if valor1 > valor2:
                return 1
            else:
                return 0
        elif tokenLogico == '>=':
            if valor1 >= valor2:
                return 1
            else:
                return 0
        return valor1

    def restoRel(self):
        if self.tokenEsperadoEncontrado(tt.COMPARA):
            self.consome(tt.COMPARA)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        elif self.tokenEsperadoEncontrado(tt.DIFERENTE):
            self.consome(tt.DIFERENTE)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        elif self.tokenEsperadoEncontrado(tt.MENOR):
            self.consome(tt.MENOR)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        elif self.tokenEsperadoEncontrado(tt.MENORIGUAL):
            self.consome(tt.MENORIGUAL)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        elif self.tokenEsperadoEncontrado(tt.MAIOR):
            self.consome(tt.MAIOR)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        elif self.tokenEsperadoEncontrado(tt.MAIORIGUAL):
            self.consome(tt.MAIORIGUAL)
            valor = self.addfunc()
            self.semantico.testaTipoInteiro(valor, self.tokenAtual.linha)
            return valor
        else:
            pass

    def addfunc(self):
        total = None
        valor1 = self.multfunc()
        tokenOperador = self.tokenAtual.lexema
        valor2 = self.restoAdd()
        if tokenOperador == '+':
            total = valor1 + valor2
        elif tokenOperador == '-':
            total = valor1 - valor2
        if valor1 is not None and valor2 is None:
            return valor1
        elif valor1 is None and valor2 is not None:
            return valor2
        elif total is not None:
            return total

    def restoAdd(self):
        if self.tokenEsperadoEncontrado(tt.ADD):
            self.consome(tt.ADD)
            valor = self.multfunc()
            self.restoAdd()
            return valor
        elif self.tokenEsperadoEncontrado(tt.SUBT):
            self.consome(tt.SUBT)
            valor = self.multfunc()
            self.restoAdd()
            return valor
        else:
            pass
    
    def multfunc(self):
        total = None
        valor1 = self.uno()
        tokenOperador = self.tokenAtual.lexema
        valor2 = self.restoMult()
        if tokenOperador == '*':
            total = valor1 * valor2
        elif tokenOperador == '/':
            total = valor1 / valor2
        elif tokenOperador == '%':
            total = valor1 % valor2
        if valor1 is not None and valor2 is None:
            return valor1
        elif valor1 is None and valor2 is not None:
            return valor2
        if total is not None:
            return total

    def restoMult(self):
        if self.tokenEsperadoEncontrado(tt.MULT):
            self.consome(tt.MULT)
            valor = self.uno()
            self.restoMult()
            return valor
        elif self.tokenEsperadoEncontrado(tt.DIV):
            self.consome(tt.DIV)
            valor = self.uno()
            self.restoMult()
            return valor
        elif self.tokenEsperadoEncontrado(tt.MODULO):
            self.consome(tt.MODULO)
            valor = self.uno()
            self.restoMult()
            return valor
        else:
            pass

    def uno(self):
        if self.tokenEsperadoEncontrado(tt.ADD):
            self.consome(tt.ADD)
            valor = self.uno()
            return valor
        elif self.tokenEsperadoEncontrado(tt.SUBT):
            self.consome(tt.SUBT)
            valor = self.uno()
            return valor
        elif (self.tokenEsperadoEncontrado(tt.NUMINT) or
              self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
              self.tokenEsperadoEncontrado(tt.ABREP)):
            valor = self.fator()
            return valor

    def fator(self):
        if self.tokenEsperadoEncontrado(tt.NUMINT):
            valor = int(self.tokenAtual.lexema)
            self.consome(tt.NUMINT)
            return valor
        elif self.tokenEsperadoEncontrado(tt.NUMFLOAT):
            valor = float(self.tokenAtual.lexema)
            self.consome(tt.NUMFLOAT)
            return valor
        elif self.tokenEsperadoEncontrado(tt.ABREP):
            self.consome(tt.ABREP)
            self.atrib()
            self.consome(tt.FECHAP)

    def call(self):
        self.consome(tt.ABREP)
        self.explist()
        self.consome(tt.FECHAP)

    def explist(self):
        if (self.tokenEsperadoEncontrado(tt.NEGAR) or
            self.tokenEsperadoEncontrado(tt.ADD) or
            self.tokenEsperadoEncontrado(tt.SUBT) or
            self.tokenEsperadoEncontrado(tt.NUMINT) or
            self.tokenEsperadoEncontrado(tt.NUMFLOAT) or
                self.tokenEsperadoEncontrado(tt.ABREP)):
            self.exp()
            while True:
                if self.tokenEsperadoEncontrado(tt.VIRG):
                    self.consome(tt.VIRG)
                    self.exp()
                else:
                    break

if __name__== "__main__":

   nome = 'exemplo.toy'
   parser = Sintatico()
   parser.traduz(nome)