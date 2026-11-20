# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：素のLLMは一般的なAIプログラミング・リスキリング系講座における3レベルの定義を回答したが、エージェントはglossary.jsonの内容を元に回答を行った。
- `--trace` で見えたツール呼び出し（ツール名と引数）：search_glossary({'query': 'LoRA'}),search_glossary({'query': 'QLoRA'})
- 1つの質問での LLM 呼び出し回数（`requests`）：2
- 追加したツールと、docstring に書いた説明：make_quizを追加した。docstringには、「指定した回の用語から1つを選び、確認問題と答えを返す。「第2回の確認問題を出して」のように、復習用の問題を求められたときに使う。戻り値のJSONには必ず question と answer を含める。問題文だけで答えを省略しない。」という説明文を記載した。

## 宿題

- 取り組んだレベル：実装
- やったこと：save_learning_logツールを追加し、過去にmake_quizツールで出題された問題と答えをloearning_log/フォルダに保存するようにした。保存する際は、Pydantic AIのrequires_approval=Trueを使い、利用者の確認を挟むようにした。
- 結果：意図した通りの実装ができた。
- 気づき・疑問：LLMからの揺らぎのある回答をdocstringでいかに制限し意図した動きにしていくかが重要であることに気づいた。