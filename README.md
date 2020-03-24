# Yahoo_finance_scraper

**Explicação em português mais abaixo.**

**Code for webscraping Yahoo finance page for detailed data on stocks.**

**Made by: github.com/Iuryck**

**Email: iurycks4@gmail.com**

**The Jupyter notebooks with detailed explanation are in portuguese and the final codes (Load_Bovespa and yahoo_scraper) are
in english. If anyone is willing to help creating translated copies of this feel free to ask so. Proper credit will be given.**

**I wrote the code and explanations this way to try and make for anyone to understand essentially because I live in Brazil.**

# Files

## -> "Coleta de dados" 1,2 and 3

**In these files I explain the best I could the step by step approach in order to get to the final functional code, in portuguese.
Each file is a group of data from some page being scraped in a different way, with the purpose of joining the knowledge/code of the
3 files together and make the final code. In these I use stocks from the IBOVESPA group as example, but the code works for any stock
listed in the Yahoo finance page (with the exception of the code part where I get the updated companies in the IBOVESPA 
in Coleta_de_dados1).**

## -> Load_Bovespa

**This is the code for which I started all this in the first place. Get data from all the companies in the IBOVESPA. This code will
get the updated list of the stocks in the IBOVESPA group and then iterate through each one grabbing detailed data about them. This
is the product of the "Coleta_de_dados" files.** 
**Doesn´t require any arguments, as long as Pyhton and the used libraries are installed, it should be just a click-n-run. Stock data will be saved 
in the same directory as the code itself in a file called** *B3_stock_dfs*.

## -> yahoo_scraper

**Functions the same way Load_Bovespa does, but instead of looking for the IBOVESPA stocks, it receives a CSV file with a list of stocks,
then iterates through all of them and grabs the detailed data. The CSV file can have any data but the list with the stocks MUST be the
second column (index + stocks column). For now, it´s just how the code works, sorry if i´m not THE all mighty dev. Feel free to suggest
changes for this.**

### Usage:
  *yahoo_scraper.py -i file/path.csv*  **or** *yahoo_scraper.py --ifile= file/path.csv*
  **Receives the path for the CSV file that contains the list of stocks for which it will iterate and collect data.**
  
  *yahoo_scraper -h* **or** *yahoo_scraper --help*
  **Shows the help message, explaining how to use the code:**
  
  
        Usage: yahoo_scraper.py -i <stock/list/file/path.csv>


         File with desired stocks must be a csv file and be the second column (index counted) in the csv file


         __How list is passed and used__



         def get_tickers(stock_list):

            list =  pd.read_csv(stock_list)

            try:
                tickers = [c for c in list[list.columns[1]]]
            except Exception as e:
                print(e)
                sys.exit(1)

            ....

            for ticker in (tickers):


  
  **Maybe in the future I may add a code for daily updating on these files, and the yahoo_scraper would generate the code for the
  stocks automatically, but for now it´s what it is. If anyone wants to help on the code feel free to email me, using Github as topic.**
  
  
# Yahoo_scraper (PT-BR)  



**Código que faz "webscrap" na página do Yahoo finance para coletar dados detalhados de ações.**

**Os arquivos "Jupyter notebooks" (Coleta de dados 1,2 e 3) com explicações detalhadas estão em português e os códigos finais
(Load_Bovespa e yahoo_scraper) estão em inglês. Se alguém estiver disposto a ajudar criar cópias traduzidas de um ou outro sinta-se
livre de pedir para pedir. Os devidos créditos serão dados.**

**Eu escrevi os códigos e as explicações assim para tentar fazer para qualquer um entender, essencialmente por que eu 
moro no Brasil.**

# Arquivos

## -> "Coleta de dados" 1,2 e 3

**Nesses arquivos eu expliquei o melhor que pude o passo a passo para chegar ao código funcional final, em português.
Cada arquivo é um grupo de dados de uma página sendo "scraped" (raspada) em uma maneira, com o propósito de juntar o 
conhecimento/código dos três arquivos e fazer o código final. Nesses arquivos eu uso ações da IBOVESPA como exemplo, mas
o código funciona para qualquer ação listada na página do Yahoo finance (com exceção da parte onde eu pego a lista de ações atualizadas
da IBOVESPA no arquivo Coleta_de_dados1).**

## -> Load_Bovespa

**Esse é o código pelo qual comecei tudo isso em primeiro lugar, pegar dados de todas as empresas no IBOVESPA. O código vai 
pegar uma lista atualizada das ações que estão no IBOVESPA e depois iterar por cada um, pegando dados detalhados sobre eles.
Esse é o produto dos arquivos de Coleta_de_dados.** 
**O código não requer nenhum argumento, desde que Python e as bibliotecas usadas estejam instalados, o código deve fazer tudo em um clique.
Os dados das ações serão salvos no mesmo diretório que o código dentro de uma pasta chamada** *B3_stock_dfs*.

## -> yahoo_scraper

**Funciona do mesmo jeito que o Load_Bovespa, porém ao invés de coletar dados das ações da IBOVESPA, ele recebe um arquivo CSV
com uma lista de ações, e então vai iterar por tdos eles e coletar os dados detalhados. O arquivo CSV pode ter quaisquer dados mas
a lista com as ações TEM QUE ser a segunda coluna (índice + coluna com ações). Por enquanto, é assim que o código funciona, desculpa 
não ser O mestre desenvolvedor. Sinta-se livre para sugerir melhoras nessa parte.**

### Uso:
  *yahoo_scraper.py -i caminho_para/arquivo.csv*  **ou** *yahoo_scraper.py --ifile= caminho_para/arquivo.csv*
  **Recebe o caminho para o arquivo CSV que possui a lista de ações pelo qual o código vai iterar e coletar dados.**
  
  *yahoo_scraper -h* **ou** *yahoo_scraper --help*
  **Mostra a mensagem de ajuda, explicando como usar o código:**
  
        #Uso:                      <arquivo/com/lista.csv>
        Usage: yahoo_scraper.py -i <stock/list/file/path.csv>

         #Arquivo com ações desejadas deve ser um arquivo csv e precisa ser a segunda coluna (contando índice) dentro do arquivo
         File with desired stocks must be a csv file and be the second column (index counted) in the csv file

          #Como a lista é passada e usada
         __How list is passed and used__



         def get_tickers(stock_list):

            list =  pd.read_csv(stock_list)

            try:
                tickers = [c for c in list[list.columns[1]]]
            except Exception as e:
                print(e)
                sys.exit(1)

            ....

            for ticker in (tickers):


**Talvez no futuro eu adicione um código que atualize informações diárias, usando o yahoo_scraper para gerar esse código. Mas por enquanto
é o que é. Se alguém quiser ajudar no código basta me mandar um email com o assunto GitHub.**


