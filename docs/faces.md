# Portrait codes `{face:XXXX}`: who is speaking

Built from `script/event/*.json` by reading every face id's lines and the lines around them (2026-10-11). Ids are hex. B = Black Book, R = Red Book. Most ids are the same character in both books. The exceptions are **0000/0001** (the current book's hero and partner), **003A/003B** (they swap between books), and **0017/0018** (the same role played by a different boss in each book).

Names: glossary spelling where the glossary lists one. † = not in the glossary; the spelling given is the mainline SMT name, or Hepburn when there isn't one. The controller should confirm it before adding it.

| face | book(s) | character (JP) | English name | gender | speech style | conf | evidence |
|---|---|---|---|---|---|---|---|
| 0000 | B | 甲斐刹那 | Setsuna Kai | M | boyish, blunt; オレ/おれ, だ/ぜ | high | 「何の話だ？・・・お前は誰だ！？」 B:26C04 |
| 0000 | R | 要未来 | Mirai Kaname | F | girlish, lively; 私, わよ/の | high | 「私のパパはこの魔界のどこかにいるはずなのよ」 R:29134 |
| 0001 | B | クール | Cool | M | rough, cocky; オレ, ぜ | high | 「アッ、思い出したゼ！…オレが封印されたのは！」 B:2EF08 (see note on B:277C8) |
| 0001 | R | ベール | Veil | F | perky, bossy; 私/ワタシ, わよ | high | 「私に乗れば氷の上だってへっちゃらよ！」 R:45D90 |
| 0003 | R | 甲斐刹那 | Setsuna Kai (guest in Red) | M | boyish; おれ/オレ | high | 「おれは大魔王にさらわれた弟を探しに…」 R:3BD20 |
| 0004 | B | 要未来 | Mirai Kaname (guest in Black) | F | girlish; 私, わ/ね | high | 「あなたが、デビルチルドレンなの？」 B:39334 |
| 0005 | R | クール | Cool (guest in Red) | M | rough; オレ | med | 「オレに何か用か？」 R:33D1C (next to Setsuna 0003) |
| 0006 | B,R | ベール | Veil (R: intro before naming; B: guest) | F | perky; ワタシ, ♥ | high (R) / med (B) | 「ワタシはベール♥」 R:28250; B:320A4 「私に何か用？」 |
| 0007 | B,R | タカジョー・ゼット | Zett Takajo | M | gentle, friendly; ボク/ぼく, きみ | high | 「初めまして・・・ボクはタカジョー・ゼット！」 B:27920 |
| 0008 | B,R | 甲斐永久 | Nagahisa Kai | M | soft, polite; ぼく, 兄さん, です/ます to others | high | 「兄さん、ぼくの父さんは大天使ミカエルなんです」 B:3118C |
| 0009 | B,R | エレジー | Elegy† | F | haughty brat; あたし/私 | high | 「あたしはエレジーよ」 B:38C2C |
| 000A | R | ユーキ | Yuki | M | friendly boy; ぼく | high | 「ぼくはユーキっていうんだけど」 R:27578 (the game spells it ユーキ, not ユキ) |
| 000B | R | ソウタ | Souta | M | punk; おれ, ぜ, くそー | high | 「おれはソウタってんだ！」 R:27F8C |
| 000D | B,R | ルシファー | Lucifer | M | dignified father; 私, のだ | high | 「私は、この世界を次の時代に進めるプログラム…」 B:3EC18 (addressed 大魔王ルシファー at B:3E844) |
| 000F | B,R | アゼル | Azel | M | villain; オレ, アゼル様 | high | 「このアゼル様に会いに来た事を…」 B:35218 |
| 0010 | B,R | ヘル | Hel† | M-coded speech | lordly; わし (R), キサマ-style taunts | high | 「この魔王ヘルがデビルチルドレンの力を…」 B:481B0 |
| 0011 | B,R | ダイアナ | Diana† | F | gyaru slang; チョーヤバイ, katakana endings | high | 「えっ！ダイアナはワタシよ！」 R:2A778 |
| 0012 | B,R | ダスト | Dust† | M | tough guy; オレ, つえーな (fake-polite while disguised) | high | 「私の名前はダストですよ」 R:2A454 |
| 0014 | B,R | ビビサナ (ラセツ王) | Vibhishana† | M | courteous; 私/わたくし, 様 | high | 「私は、ラセツ王ビビサナ」 B:2CADC |
| 0015 | B,R | ヴリトラ (シュラ王) | Vritra† | M | gruff warrior; わし/オレ | high | 「わしはシュラ族の王・ヴリトラ」 R:2CD90 |
| 0016 | B,R | インドラ (デーバ王) | Indra† | M | lordly; わし | high | 「わしはデーバ族の王・インドラ」 R:2CE10 |
| 0017 | R | パイモン | Paimon† | F | haughty lady; わよ | high | 「弱すぎー・・・」 R:2CCAC (Mirai: 「そのパイモンが何の用なの？」 R:2CC88) |
| 0018 | B | アバドン | Abaddon† | M | menacing general; だ, later old-man じゃ | high | 「弱すぎる・・・」 B:2C92C, right after 「魔界しょうぐん、アバドン！？」 |
| 0019 | B,R | イシス | Isis† | F | regal, teasing; 私, わ/よ | high | 「あなたはこのイシス様に何が聞きたいの？」 R:38B48 |
| 001A | B,R | ベリアル | Belial† | M | moody: rough when angry (オレ, カエセヨー), otherwise smarmy-polite (わたくし, ますぞ) | high | 「金のリンゴパイ盗んだろ！」 B:312EC |
| 001B | B,R | ダハーカ | Azi Dahaka† (text says only ダハーカ) | M | braggart dragon; オレサマ | high | 「オレサマは無敵のドラゴンダハーカ様だ！」 B:321E8 |
| 001C | B,R | クロークルワッハ | Crom Cruach† | M | braggart dragon; オレサマ | high | 「…ドラゴンクロークルワッハ様だ！」 B:32400 |
| 001D | B,R | ニーズホッグ | Nidhoggr† | M | braggart dragon; オレサマ | high | 「…ドラゴンニーズホッグ様だ！」 B:3230C |
| 001E | R | ニスロク | Nisroc† | M | chirpy cook | high | 「金のリンゴパイ？オッケー！まかせてよ」 R:31314 |
| 001F | B | キングフロスト | King Frost† | M | ～ホー tic | high | 「オレ、キングフロスト！！」 B:30BB4 |
| 0020 | B,R | マモン | Mammon† | M | Kansai merchant; わて, や/で | high | 「わてがマモンや」 B:3353C |
| 0021 | B,R | ラハブ | Rahab† | M | old scholar; ワシ, のだ | high | 「ワシはラハブ」 B:32D58 |
| 0022 | B | ウリエル | Uriel† | M | cold, polite; わたくし, なさい | high | 「わたくしは大天使、ウリエル」 B:310FC |
| 0023 | R | ラファエル | Raphael† | M | polite; わたくし | high | 「わたくしは、大天使ラファエル」 R:31010 |
| 0024 | B,R | ミカエル | Michael† | M | stern, polite; 私, です/ます | high | 「大魔王ルシファー！ひさしぶりですね」 B:3E844 |
| 0027 | B,R | ホシガミ | Hoshigami† | F-coded | serene goddess; 私, わ/なの | med | 「ラグナロクを起動させて私を起こしに来たのは、誰？」 B:3B138 |
| 0028 | B,R | ベリト | Berith† | M | gruff; オレ, だ | high | 「このベリトとフェゴールそしてゼブルは兄弟なのだ」 B:43F30 |
| 0029 | B,R | フェゴール | Phegor† (Hepburn Fegōru) | M | cool; さ endings | high | 「わが名はフェゴール」 B:3F218 |
| 002A | B,R | ゼブル | Zebul† (Zett's true form) | M | boyish; ぼく | high | 「ここでのぼくの名は、ゼブルさ」 B:3F47C |
| 002B | B | ガルム | Garm† | M | thug; オレ, ヘヘッ | high | 「オレはしょうきんかせぎのハンター、ガルム！！」 B:292D8 |
| 002C | B | フェンリル | Fenrir† | M | thug boss; おめえ | high | 「行け！ガルム！」 B:2E324 (Garm calls him フェンリルのアニキ, B:2E584) |
| 002E | R | フレスベルク | Hresvelgr† | F-coded | sassy; 私, わよ | med | 「やるわよ、ソウタ！」 R:2ED48 (Veil: 「フレスベルク！ソウタ！」 R:2EB14) |
| 0034 | B | スフィンクス? | Sphinx† | — | growl only | med | 「グルルルルルル」 B:462F8, right after Sphinx joins |
| 003A | B | ドクター・フランケン | Dr. Franken† (fusion lab) | M | gruff scientist; オレ | high | 「…ドクター・フランケン！」 B:43FEC |
| 003A | R | (unnamed) trainer / Moai keeper | Trainer | M | casual; ぜ | med | 「仲魔をきたえていくか？」 R:3AA60 |
| 003B | B | (unnamed) trainer / Moai keeper | Trainer | M | casual | med | 「モアイは元気かい？」 B:46310 |
| 003B | R | パラレル・スス | Parallel Susu† (fusion lab) | M | pidgin; ワタシ, ～ネ | high | 「ワタシは…パラレル・ススという者ネ」 R:42D18 |
| 0045 | B,R | 大魔王 (Azel posing as Lucifer) | Great Demon King† (Daimaō) | M | B: arrogant おれ/オレ様; R: smooth and polite (to manipulate Mirai) | high | 「わざわざ、この大魔王に会いに来るとは」 B:34D44 |
| 0049 | B | (unnamed) Harajuku underground boss | — | M | villain; オレ | med (role) / low (name) | 「さすがだなデビルチルドレン」 B:49BFC (same lines as R 004A) |
| 004A | R | (unnamed) Harajuku underground boss | — | M | villain; オレ | med | 「人間をほろぼし地上をデビルの物とする…」 R:3D09C |
| 004B | B | ニタニタ | Nitanita† | — | giggles ニタニタ | high | 「あっ、それワライブクロ！」 B:41750, then 「ニタニタが仲魔になった」 |
| 004C | R | ヒポグリフ | Hippogriff† | F | cheerful; 私 | high | 「あーっ、{hero}じゃない！」 R:4085C (Veil: 「やっぱりヒポグリフだわ！」) |
| 004D | B | オルトロス | Orthrus† (Cool's little brother) | M | kid brother; ぼく, 兄さん | high | 「あーっ、兄さんだ！」 B:2F004 (Cool: 「やっぱりオルトロスだ！」) |
| 004E | B | スカルクラウン | Skull Clown† | M | polite; ぼく | high | 「やっと、出られたあぁーー！！」 B:42104, joins B:421D8 |
| 004F | B,R | ブラックラジャー | Black Rajah† | M | dazed, then friendly; おれ→ぼく | high | 「おれは・・・ダレダ？」 B:42554, joins B:428B0 |
| 0050 | B | ハーピー | Harpy† | F | sweet singer; ♥ | med | 「これは心をいやす歌なの」 B:42614 |
| 0051 | B,R | (unnamed) lonely demon kid who wants a Nessie | — | — | childlike; ボク | low | 「あのね、ボク１人ぼっちなの」 B:42EC4; Nessie's own intro also uses 0051 at B:42B18 |
| 0052 | B,R | コトダマ? | Kotodama† | — | playful; ぼく | med | 「見つかっちゃったね」 B:43214, joins B:432F0 |
| 0053 | B | デービーくん | Davy-kun† (robot) | M | robotic, katakana | high | 「ボク、デービーくん・・・ボク、仲魔ニナルヨ」 B:4368C |
| 0054 | B | ネコのナマモノ | Cat Namamono† | M | ぼく | high | 「ぼくはネコのナマモノさ」 B:43170 |
| 0055 | B | タヌキのナマモノ | Tanuki Namamono† | F | lazy drawl; ～よー | high | 「私はタヌキのナマモノよ」 B:43A54 |
| 0056 | B,R | デビダスマスター | Devidas Master† (quiz host) | M | professor; わたし, だ | high | 「わたしはデビルの研究家デビダスマスター！」 B:44134 |
| 0057 | B | ぶんぶくちゃがま | Bunbuku Chagama† | — | ボク | high | 「ボクはぶんぶくちゃがま」 B:2A97C |
| 0058 | B | モアイ | Moai† | — | grunts ウゴー | med | 「ウゴー！ウゴー！」 B:2C10C |
| 0065 | B | ろくろくび | Rokurokubi† | F | あたし | high | 「あたしはろくろくびよ」 B:49848 |
| 0066 | B | カグヤひめ | Kaguya-hime† | F | flirty; ダーリン♥ | high | 「わたしはカグヤひめよ」 B:49D08 |
| 0067 | B,R | けうけげん | Keukegen† | M | shy; ボク | high | 「ボク、けうけげん！」 B:34CFC |
| 0068 | R | ブラウニー | Brownie† | M | cheeky; ボク | high | 「ブラウニーっていうりっぱな名前があるんだぞ！」 R:434E4 |
| 0069 | B | きよひめ | Kiyohime† | F | clingy; わたし | high | 「わたしはきよひめ、よろしくね」 B:49F54 |
| 00FF | B,R | — | no portrait | — | narration, item/system text, choices, hero's thoughts, not-yet-named speakers | high | 「金色のメシアのツノを手に入れた」 B:2A468; 「ボク、みんなに嫌われてるんだ」 B:34BA8 (Keukegen before his intro) |
| 0570 | R | — | invalid / leftover | — | — | low | `{face:0003}{face:0570}？・・ほら、あの強気な・・・` R:3AA38 (only use; probably dead data) |

## Notes

- **Ids shared by several kings.** The tournament lines in Marble Land (「そうです！{f8}様が一番強いのですから！」, the medicine line, and others) appear under 0014, 0015 and 0016. The game picks the copy for whichever king is speaking or won. Translate each copy in that king's voice.
- **Book-swapped ids.** 0017 (R, Paimon) and 0018 (B, Abaddon) have the same lines in different voices; keep the gender of each. 003A and 003B swap roles between the books (fusion lab owner and trainer).
- **No face code ≠ same speaker.** About half the messages (1533 of 3081) have no face code. They are mostly:
  - talk-to NPCs that have no portrait (625, all starting `{ee}`);
  - menus and choices (108, lines starting with a full-width space);
  - item, join and system narration (~120);
  - about 680 other lines from portrait-less speakers: shopkeepers, TV news, minor demons, Cool's first lines (「オレはイヌじゃない！！」 B:27804), and sometimes the hero (「・・・！？・・・オレを知っているのか？」 B:27380).

  They rarely continue the previous portrait's speaker. Decide the speaker from context, never by carrying the last face forward.
- **Faces change mid-message.** The face can switch inside a message, e.g. B:49D08 goes `{face:0000}` → `{face:00FF}` → `{face:0066}`. Each face covers the text after it.
- **Likely original bug.** B:277C8 「ケンジュウから犬が出た！しかも、しゃべった！！」 is Setsuna's line but has Cool's face 0001; the Red Book equivalent, R:282A4, uses 0000. Check it in the emulator before "fixing" anything.
- **`{ee}` meaning.** All 778 uses are at the very start of a message, and nearly all are talk-to-NPC text or repeat lines on re-talking (「戻って来たんだね！」). It most likely marks a message started by talking to an NPC (the NPC turns to face you, or a generic talk box). Confidence: med.
- **`{ea}` meaning.** In 40 of 43 uses it comes right before a silent beat 「・・・・・」; the rest come before the mirror and box narration that opens the game. It is probably a dramatic pause or a no-voice/slow-text toggle. Confidence: low. Keep it where it is.
- **`{f8}` / `{hero}` meanings look reversed** from the brief:
  - `{f8}` = the protagonist's name: 「{f8}はノルンのカギを使った」 B:3EE90, Cool's 「{f8}、気をつけろ！」;
  - `{hero}` = the partner's name: 「{hero}はすっかり元気になった！！」 B:2BA58 after 「この薬を{hero}どのに」; Hippogriff's 「あーっ、{hero}じゃない！」 R:4085C.
- **Glossary follow-ups.**
  - Veil's kana is confirmed as ベール (R:28250).
  - Yuki is ユーキ in this script; the glossary's JP column says ユキ.
  - Many demon names (†) still need glossary entries.
