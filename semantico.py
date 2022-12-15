from lexico import TipoToken as tt, Token, Lexico

class Semantico:

    def __init__(self):
        self.lex = None
        self.deuErro = False

    def erroSemantico(self, msg, linha):
        print('ERRO SEMANTICO [linha %d]: "%s"' % (linha, msg))

    # Verifica se a variavel foi declarada no codigo
    # ou se foi utilizada sem ser declarada
    def testaVarNaoDeclarada(self, var, linha, tabsimb):
        if self.deuErro:
            return
        if not tabsimb.existeIdent(var):
            self.deuErro = True
            msg = "Variavel " + var + " nao declarada."
            self.erroSemantico(msg, linha)
            quit()

    # Verifica se o tipo da variavel eh inteiro
    def testaTipoInteiro(self, var, linha):
        if self.deuErro:
            return
        if type(var) is not int:
            self.deuErro = True
            msg = "Indice " + str(var) + " nao eh do tipo inteiro."
            self.erroSemantico(msg, linha)
            quit()

    def traduz(self, nomeArquivo):
        if not self.lex is None:
            print('ERRO: Já existe um arquivo sendo processado.')
        else:
            self.deuErro = False
            self.lex = Lexico(nomeArquivo)
            self.lex.abreArquivo()
            # fim do reconhecimento do fonte
            print(self.lex)

            self.lex.fechaArquivo()
            return not self.deuErro

if __name__ == '__main__':
    print('Semantico\n')

    # nome = input("Entre com o nome do arquivo: ")
    nome = 'exemplo.toy'
    parser = Semantico()
    parser.traduz(nome)
    #if ok:
    #    print("Arquivo sintaticamente correto.")