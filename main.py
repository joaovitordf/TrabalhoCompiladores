import sys
import getopt

#
#    Testa o tradutor
#

"""
// Nome Discente: João Vitor Dias Fernandes
// Matrícula: 0056152
// Data: 14/12/2022


// Declaro que sou o único autor e responsável por este programa. Todas as partes do programa, exceto as que foram fornecidas
// pelo professor ou copiadas do livro ou das bibliotecas de Aho et al., foram desenvolvidas por mim. Declaro também que
// sou responsável por todas  as eventuais cópias deste programa e que não distribui nem facilitei a distribuição de cópias. 

///////////// Leia e depois apague  os comentários abaixo //////////////////////////

// Escreva um comentário no início do arquivo fonte para indicar O QUE o código faz
// Coloque comentários no seu código de modo a explicar o que está sendo feito
// Se utilizar ou basear seu código em alguma fonte externa, explicite este fato. Se não houver nenhuma menção em contrário 
// vou considerar que o código foi baseado me descrito em Aho et al.
"""

from sintatico import Sintatico

# Salva a tabela de simbolos através de comando no terminal
# Exemplo: python main.py -t teste.txt
# A funcao comandoTerminal teve como base o codigo disponibilizado no site:
# https://www.geeksforgeeks.org/command-line-arguments-in-python/
def comandoTerminal(argv):
    arg_terminal = ""
    arg_help = "{0} -t <nometexto>".format(argv[0])
    
    try:
        arguments, values = getopt.getopt(argv[1:], "ht:", ["help", "terminal="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif currentArgument in ("-t"):
            arg_terminal = currentValue

    return arg_terminal

if __name__ == '__main__':
    print('Tradutor Toy \n')
    # nome = input("Entre com o nome do arquivo: ")
    nome_arquivo = comandoTerminal(sys.argv)
    nome = 'exemplo.toy'
    parser = Sintatico()
    ok = parser.traduz(nome)
    if nome_arquivo != '':
        tabela_simbolos = parser.tabelaSimbolos()
        arquivo = open(nome_arquivo, 'w')
        arquivo.write(str(tabela_simbolos))

    if ok:
        print("Arquivo lexicamente correto.")
        print("Arquivo sintaticamente correto.")
        print("Arquivo semanticamente correto.")
