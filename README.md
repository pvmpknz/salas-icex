# salas-icex

fiz isso pra achar sala vazia no ICEx sem ficar andando de porta em porta.

mostra a hora de Brasília e quais salas tão livres agora, tirando da grade do semestre (um PDF).

https://pvmpknz.github.io/salas-icex/

## semestre novo

1. põe o pdf novo na pasta com o nome `grade.pdf`
2. `pip install -r requirements.txt` (só na primeira vez)
3. `python gerar.py grade.pdf --semestre 2027/1`
4. sobe o `index.html` novo aqui no github

## obs

- não sabe de feriado nem de troca de sala
- sala livre não é sala aberta, confere na porta
- projeto de fim de semana, pode ter bug
