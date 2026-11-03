# Hardstart Films — Habilidade local de edição

## Quando usar
Ao criar ou editar filmes deste projeto. Ler `design.md` integralmente e o `project.md` do vídeo antes de trabalhar. Estas preferências se aplicam à produção própria; não substituem a necessidade de verificar ferramentas e licenças disponíveis.

## Preferências persistidas
Planejar em português; produzir voz, textos, legendas e metadados em inglês. Animação 2D escura, expressiva e simples, com personagem próprio. Montagem dinâmica, cortes motivados, inserts e interação real com objetos. Incluir 1 ou 2 gráficos/diagramas explicativos por filme, sem inventar dados. Construir trilha, ambiência e foley, com efeitos sincronizados e pausas dramáticas.

## Pipeline
1. Ler fontes e decisões anteriores. Identificar o que já está pronto e o que é apenas proposta.
2. Escrever roteiro inglês e shot list com ação, enquadramento, duração estimada, som, luz e transição.
3. Planejar 1 ou 2 gráficos nos momentos em que explicam a mensagem; distinguir dados de metáfora.
4. Consolidar personagem e cenário; criar animatic e revisar a ação.
5. Produzir voz com ferramenta autorizada, ajustar montagem à fala e animar contatos, gestos e reações.
6. Selecionar trilha e efeitos com direitos verificados; preferência por Epidemic Sound se houver acesso legítimo. Sem integração disponível, usar arquivos licenciados enviados pelo usuário. Nunca declarar conexão sem teste bem-sucedido nem solicitar senha em chat.
7. Sincronizar efeitos às ações, mixar stems e aplicar legendas depois das sobreposições.
8. Rever imagem e som completos; medir loudness e pico, checar sincronização, legibilidade e decodificação.
9. Salvar decisões e pendências em `edit/project.md`; entregar versão claramente identificada. Publicação exige instrução separada.

## Ferramentas locais existentes
FFmpeg e ffprobe no PATH. Python: `/workspace/video-tools/venv/bin/python`. Auxiliares: `/workspace/video-tools/video-use/helpers/`. Ler as instruções da ferramenta antes de executar. Trabalhos em `/workspace/video-projects/<nome>/edit/`; originais preservados. Animação inicial de disciplina: `/workspace/video-projects/hardstart-discipline/edit/create_animatic.py`.

## Pendências reais
O primeiro filme tem animatic silencioso; narração, trilha, efeitos e gráficos novos ainda precisam ser produzidos. Nenhuma integração com Epidemic Sound foi encontrada ou autenticada. Nenhuma licença de faixa do serviço foi verificada. A preferência do usuário não deve ser reportada como implementação concluída. A série nova tem voz sintética local; os primeiros animatics antigos continuam sem voz até atualização específica.


## Duração e qualidade — atualização confirmada
O usuário rejeitou a prévia básica de dois minutos. Para o vídeo de procrastinação, a nova versão deve ter no mínimo 5 minutos, com história ampliada, mais ação, variedade de enquadramentos, dois gráficos integrados e desenho de som. Não alongar cenas ou repetir blocos apenas para cumprir duração. Animação e narração continuam requisitos de acabamento; não chamar um workprint sem voz de filme final.


## Narração e série de dez filmes
Piper local funcional: runtime legado em `/workspace/video-tools/piper-local/piper/piper`; runtime Python em `/workspace/video-tools/tts-venv/bin/python`. Modelo usado: `/workspace/video-tools/piper-local/libritts/en-us-libritts-high.onnx`, voz inglesa sintética speaker0. Card oficial informa dataset LibriTTS, CC BY4.0; incluir atribuição. Ryan, Danny e Amy não são opções aprovadas neste projeto: as fontes testadas tinham restrições não comerciais ou licença insuficientemente clara. O adapter `hardstart-season-01/edit/engine/synthesize.py` limita threads ORT para evitar saturar os4CPUs.

Série em `/workspace/video-projects/hardstart-season-01/edit/`, com10 histórias distintas. Cada episódio deve ter pelo menos5min de duração real, dois diagramas conceituais, voz inglesa, motivos musicais/SFX próprios, cortes e interação. Roteiros, identidades, origem das evidências e verificações ficam separados. Os temas usam evidências dos prints, não um ranking ao vivo. Não afirmar render/voz/licença/publicação sem teste.

O visualizador deste chat não entregou MP4s por links locais. Após autorização do usuário, funcionou hospedar arquivos em branches separadas de `pv845753-create/codex-chat-gpt-1` e compartilhar links raw.githubusercontent.com verificados. Não confundir entrega de prévias pelo GitHub com publicação final no YouTube. Não enviar novos materiais externos sem escopo autorizado na conversa.
