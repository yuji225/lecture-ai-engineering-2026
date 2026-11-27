# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前： glossary_search_glossary
- STEP 2 の [tool call]： glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]： fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]： aws_aws___search_documentation({'search_phrase': 'Amazon S3 バージョニング 概要', 'topics': ['general']}), aws_aws___search_documentation({'search_phrase': 'Using versioning in S3 buckets', 'topics': ['general']})
- 気づき・疑問： 前回までtools.pyで定義したツールをagent.pyから直接呼び出して実行していたことを考えると、講義でも述べられていた通り、エージェントが多く動く環境ではエージェント内で個別にツールを定義して使用するより、ツールはMCPサーバーから提供する構成にする方が効率的だと実感した。MCPサーバーで権限を最小限に絞るべきという話があったが、read権限であってもreadできる範囲について人・グループ・エージェント単位で変えたい場合はあるはずで、どういった考え方でそれを設計していくのがベストか疑問に思った。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：発展
- やったこと：
    - VS CodeのMCPサーバーを設定した。(公式URL：https://code.visualstudio.com/docs/agent-customization/mcp-servers)
    VS Codeのmcp-config.json有効範囲は、公式URLに従いGlobalを設定しているため、この環境内にある複数Workspaceにまたがり使用できるようになっている。
    - 公式URLに記載のあるMicrosoft Learn(https://learn.microsoft.com/api/mcp)を指定した。設定は/home/vscode/.copilot/mcp-config.jsonに記載される。
    - 「copilot mcp enable microsoftLearn」コマンドにて、VS CodeのTerminalからMCP:microsoftLearnのツールを使用した回答が可能となった。
    - 演習STEP4と同じURL接続する方法で、app/mcp_server.jsonに"microsoftLearn": {"url": "https://learn.microsoft.com/api/mcp"}を追加して、app.mcp_agentからもツールを使用できるようにした。
- 結果：VS CodeのTerminalから「copilot -p "Azure Kubernetes Serviceについて説明して欲しい"」というコマンドを打つと、Microsoft Docs Searchツールを使ってMicrosoft公式ドキュメントの情報を使った回答が生成された。「uv run python -m app.mcp_agent --trace "Azure Kubernetes Serviceについて説明して欲しい"」というコマンドを打つと、[tool call]   microsoftLearn_microsoft_docs_search({'query': 'Azure Kubernetes Service what is AKS'})が動き、回答が生成されることを確認した。
- 気づき・疑問：/home/vscode/.copilot/mcp-config.jsonは公式URLの手順に則って作成したが、"tools": ["*"]という指定があり、呼び出せるツールを制限することが出来るようになっていることに気づいた。外部MCPサーバー側でツールの仕様変更はありそうで、変更情報をどう入手すれば良いか疑問に思った。
