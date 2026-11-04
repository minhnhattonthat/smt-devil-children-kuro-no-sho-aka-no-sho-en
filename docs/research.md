# Research: 真・女神転生デビルチルドレン 黒の書・赤の書 (PS1, SLPM-87040)

Gathered 2026-10-11. megatenwiki.com is behind Cloudflare. Its pages were read through Wayback snapshots (`web.archive.org/web/<ts>id_/...`). MTW = megatenwiki.

## 1. Disc / Redump

| Field | Value |
|---|---|
| Redump | http://redump.org/disc/62163/ (dumper Renzukoken, added 2019-05-15) |
| Serial / EXE date | SLPM 87040 / 2002-02-19 |
| Track | 1 track, Data/Mode 2, 108103 sectors, **254258256 bytes** |
| CRC32 / SHA-1 | **c374e0c6** / **f7a3e476f595e656d5d5788a27aa6beec504a5bc**: both match ours |
| MD5 | 850ff50c9a07a261c5f42b8b67fd3244 |
| Redump filename | `Shin Megami Tensei - Devil Children - Kuro no Sho, Aka no Sho (Japan).bin` (cue CRC c909d9a2) |
| LibCrypt / anti-mod | No / No |
| Release | 2002-03-28 per psxdatacenter (MTW says 03-18). Atlus. PSN re-release 2010. https://psxdatacenter.com/games/J/S/SLPM-87040.html |

## 2. Prior translation work

| Work | Who / when | Coverage | Source |
|---|---|---|---|
| **PS1 "proto patch"** (`SMT Devil Children Black Book and Red Book PSX proto patch.xdelta`, 408291 B, kept out of git in `work/proto_patch/`, made with Delta Patcher) | **cj_iwakura** posted on X on 2026-04-10: "Have an enjoy." The download is `SMT Patches.zip` (895 KB, MediaFire). The zip apparently also holds a matching proto patch for GBA *Devil Children 2 Koori no Sho*. | Partial English. Even the sharers say "I don't know how much it translates." There's no readme or changelog. Base = Redump bin CRC c374e0c6. | https://x.com/cj_iwakura/status/2042397339994751178 ; https://www.mediafire.com/file/cea8hidojrf2fts/SMT+Patches.zip/file ; https://retrogametalk.com/repo/psx-iso/shin-megami-tensei-devil-children-kuro-no-sho-aka-no-sho-jpn/ ; https://cdromance.org/gba-roms/shin-megami-tensei-devil-children-2-koori-no-sho-japan/ |
| GBC **Black Book** English patch v1.2 | Specialagentape et al., 2021-07-28 | Full Black Book only (GBC). Quality was criticised, and text was heavily cut to fit the GB screen. | RHDN https://www.romhacking.net/translations/6163/ (403 for bots) ; MTW main page |
| GBC retranslation (WIP, stalled) | Kaisaan | Uses an older *full* English script from the original translator (permission requested). Most of the JP script is extracted, but only a few lines are inserted. Plans a wider-char font routine. | https://git.randommeaninglesscharacters.com/Kaisaan/projects (403 for bots; quoted via search snippet) |
| Font recreation of the 2021 patch | DaFont user | Bitmap font only | https://www.dafont.com/devil-children-gbc-english-patch.font |
| GBC disassembly **Tauwasser/debichiru** | Tauwasser | Disassembly of Black/Red/White (GBC), 22 commits. `charmap.asm`: **single-byte**, ０-９=$00-09, ー=$15, hiragana $1E-54, katakana $55-8B, dakuten hira $8C-A4, kata $A5-BE, 。=$BF, ・=$C8, **$0A = string end**. It also has `data/monsters/`, a likely source of the demon name list. It has no script dump or English names. **Not reusable for PS1:** the PS1 script adds kanji, so the encoding must differ (probably SJIS or a custom 2-byte table). | https://github.com/Tauwasser/debichiru ; GBC Rev A note: https://blog.tauwasser.eu/?p=352 |
| PS1 tech docs (DEVIL.PAC, font, compression) | **None found.** Searches for DEVIL.PAC / B_MAIN.EXE returned nothing. | | |

## 3. Names and terms (JP → EN)

Conventions: MTW = fan wiki (de-facto fan standard). DK = *DemiKids Light/Dark* (Atlus USA GBA 2003, the only official English release). DeviChil has **no official English release**. An unaired TMS English dub translated マカイ as "Hades" (MTW).

### People
| JP | Recommended EN | Alt / conflicts | Source |
|---|---|---|---|
| 甲斐刹那 (カイ セツナ) | **Setsuna Kai** | DK BattleNet cameo: "Serina" | MTW Setsuna_Kai |
| 要未来 (カナメ ミライ) | **Mirai Kaname** | ⚠ The brief's "葛葉未来 / Mirai Kuzuha" is **wrong**. Kuzuha = Masaki Kuzuha (葛葉, White Book protagonist). | MTW Mirai_Kaname ; Famitsu https://www.famitsu.com/news/202111/17240989.html |
| クール (Cerberus/ケルベロス) | **Cool** (Setsuna's partner) | Wikipedia: "Cerberus Cool" | MTW, Wikipedia |
| ベール? (Griffon/グリフォン) | **Veil** (Mirai's partner) | Wikipedia: "pink griffon". JP kana not confirmed: check in game. | MTW, Wikipedia |
| 甲斐永久 (カイ ナガヒサ) | **Nagahisa Kai** (Setsuna's half-brother, an Angel Child) | DK cameo: "Hisa" | MTW Nagahisa_Kai |
| タカジョー・ゼット (manga 高城絶斗) | **Zett Takajō**. MTW now prefers **Zed Takajō**. | DK cameo: "Hawk". He is really Zebul (ゼブル), ruler of Deep Hole. | MTW Zett_Takajō ; psxdatacenter |
| ルシファー | Lucifer (father of Setsuna and Mirai) | | MTW |
| ミカエル / ウリエル / ラファエル | Michael (Nagahisa's father) / Uriel / Raphael | | MTW Nagahisa_Kai |
| アゼル | Azel (main villain) | | MTW, fandom Souta |
| エレジー? | Elegy (Red Book antagonist) | JP unverified | MTW |
| ユキ | Yuki (gives Mirai her Vinecom) | | MTW main, fandom Souta |
| ソウタ | Souta (a Ratatoskr, Azel's underling, Red Book) | | https://megamitensei.fandom.com/wiki/Souta |
| フレスベルグ / イシス / ベリアル / マモン | Hresvelgr / Isis (ruler of Sand Land) / Belial / Mammon (a family friend, Fire Land) | | MTW Nagahisa_Kai, fandom |
| 甲斐つぼみ? | Tsubomi Kai (Setsuna's late mother) | JP unverified | MTW |
| ホシガミ? | Hoshigami (author of the Armageddon/Ragnarok programs) | JP unverified | MTW |

### Places
| JP | EN | Notes / source |
|---|---|---|
| 原宿 / 神宮前原宿 | Harajuku / Jingumae Harajuku | MTW Harajuku page |
| 原宿小学校 | Harajuku Elementary School | MTW |
| 現実世界 / 地上 | Real World / Surface | MTW |
| 魔界 / マカイ | **Makai** | Alt: "Demon World". DK: "Dem". SMT localizations: "Expanse". Unaired anime dub: "Hades". Recommend **Makai** (MTW, game-consistent). |
| (アイス/マーブル/サンド/フォレスト/ファイア/セントラル)ランド? | Ice / Marble / Sand / Forest / Fire / Central **Land** | MTW is inconsistent: "Sand Land" and "Forest Land" on character pages, "Ice World" etc. on the demon list. Verify the katakana in game. |
| ? | Light Palace, Deep Hole, Sanctuary, Orgel Room, Bed Town, Casino Town, Circle Gate, Vinecenter | MTW (JP unverified) |
| 原塾 | Hara-Juku (cram school pun) | MTW Harajuku trivia |

### Systems / items
| JP | EN (MTW / fan) | DK official | Source |
|---|---|---|---|
| デビルチルドレン / デビチル | Devil Children / DeviChil | **DemiKids** | Wikipedia, MTW |
| デビライザー | **Deviliser** ("Devil Riser Gun"). Fan alt: Devil Riser | **Demiloc** | MTW Deviliser |
| キングライザー | King Riser | **Kingloc** | MTW Deviliser |
| メモリーブレット / デビルコード | Memory Bullet / Devil Code | | MTW Deviliser |
| ヴィネコン | Vinecom (from the demon Vine + パソコン) | (not found) | MTW Vinecom |
| ヴィネセンター | Vinecenter | | MTW |
| コール | Call (summon/swap command) | "Summon" | MTW Deviliser |
| アクセス / ならびかえ | Access / Arrange (Vinecom menus) | | MTW Deviliser |
| 仲魔 (なかま; also ナカマ in kana) | Demon partner / ally ("nakama") | | MTW blurb |
| 合体 | Fusion. Variants: Partner Fusion, 2-Player Fusion, Rank-Up Fusion | | MTW |
| デビル | Devil (the series uses "Devil" for demons) | Demon | MTW |
| マッカ (♄) | Macca | Macca | MTW Harajuku stores |
| クラス C/E/G/K | Common / Elite / General / King class | | MTW |
| 属性 火水土金木日月 | Fire, Water, Earth, Metal, Wood, Sun, Moon | | MTW |
| 種族 | Races: God, Akuma/Devil, Divine, Oni/Ogre, Specter, Draco/Drake, Yoma, Mutant, Boss, Beast | | MTW demon list (MTW is itself inconsistent) |
| メシアの角笛? / メシアの瞳? | Messiah Horn / (Rainbow) Messiah Eye | | MTW, fandom (JP unverified) |
| グリーンホーン? / ノルンの鍵? | Green Horn / Norn Keys | | MTW (JP unverified) |
| アルマゲドン / ラグナロク | Armageddon / Ragnarok (programs) | | MTW |
| トレーナー | Trainer (stat-training NPC) | | MTW |
| ウェブネット? | Webnet (PS1 two-save link mode) / BattleNet | | MTW PS section |
| 悪魔全書 | not confirmed for this game. The demon compendium is probably on the Vinecom ("デビルを記録できる"). Verify in game. | | — |

## 4. Plot and systems summary

- **Setting:** 2000. A global black cloud and recession freeze Earth, and it snows in July in Harajuku. Both protagonists are orphaned 5th-graders and Devil Children (children of Lucifer by different mothers).
- **Black Book:** a package brings Setsuna a Vinecom, a Deviliser and the Messiah Horn. Jack Frosts (Petit Frosts on GBC) kidnap his brother Nagahisa into Makai. Setsuna follows with Cool the Cerberus.
- **Red Book:** Yuki gives Mirai a Vinecom and Deviliser. A disguised demon (Souta) steals her mother's memento, the Messiah Eye. She recovers it with Veil the Griffon and goes to Makai to find her missing father.
- **Shared story arc:** Angels (Michael, Uriel, Raphael) and Nagahisa (an Angel Child) seek the Orgel Room. The player picks Armageddon (side with the angels) or Ragnarok (Lucifer's side). Azel is the main villain. Zett/Zebul is the post-game boss of Deep Hole.
- **Battle:** 2v2. Slot 1 is always the partner, slot 2 is a demon from the active Riser. The kid doesn't fight. A wipe teleports you to the last heal point and halves your Macca (a bank exists to protect it).
- **Black vs Red:** the books share the same maps. Cool digs and walks on lava. Veil flies over cliffs, water, ice and sand. There are blue doors (Setsuna only) and pink doors (Mirai only). Fusion differs: Black uses a classic race table, and Mutants come only from accidents. Red uses Base + Additional Value and same-demon fusion (raises HP/MP, unlocks skills 4-6, some demons evolve), and Mutants appear in the wild. The Trainer's partner skill element is Fire (Black) or Wood (Red).
- **PS1 changes:** anime-style opening, then a menu to pick **Black Book / Red Book / Webnet** (Webnet links two saves on the memory card, replacing the GBC link cable). There are 3 save slots per book. Anime voice cast reprised (voiced events). The script now **uses kanji**, but name entry is still kana-only. 20 new demons: Kaguya-hime and Zeus are Black-only, Brownie and Amaterasu are Red-only. Faster walking. 270 demons in total.
- **Disc layout hypothesis (unverified, check in SYSTEM.CNF and with a debugger):**
  - `LOADM.EXE` = boot, opening (`OPEN.STR`) and the book/Webnet selection menu.
  - `LOADB/LOADR/LOADN` = loaders for `B_MAIN` (Black Book), `R_MAIN` (Red Book) and `N_MAIN` (Webnet / Net link mode, the third menu entry).
  - `B_/R_EVENT.BIN` = per-book event scripts (most dialogue).
  - `B_/R_BATTLE.BIN` = per-book battle code/data (fusion rules differ per book).
  - `DEVIL.PAC` = shared demon data and graphics archive.
  - `DEVIL.SUB` = probably voice/XA audio for the events.
  - The two books duplicate a lot, so expect most text twice (Black and Red), with shared text possibly in `DEVIL.PAC` or the EXEs.

## 5. Anime naming reference
- *Shin Megami Tensei: DeviChil* (2000-01, 50 eps, TMS). Cast: Setsuna (Showtaro Morikubo), Mirai (Yukana), Cool (Kikuko Inoue), Veil (Chiaki Ōsawa), Zed Takajō (Motoko Kumai), Lucifer (Ryōtarō Okiayu). The game PS1 reuses this cast. There's no official English; fansubs only. Episode titles use the same katakana demon names (ケルベロス, ジャックフロスト...). Source: MTW DeviChil.
- *D-Children: Light & Dark* is a different cast (Jin, Akira, Rand, Gale) and not relevant beyond terms.

## Sources
- Redump: http://redump.org/disc/62163/
- MTW (via Wayback): Devil_Children_Black_Book_and_Red_Book, Setsuna_Kai, Mirai_Kaname, Nagahisa_Kai, Zett_Takajō, Deviliser, Vinecom, Harajuku_(Devil_Children_Black_Book_and_Red_Book), Makai, DeviChil, Demons_in_Devil_Children_Black_Book_and_Red_Book
- Wikipedia: https://en.wikipedia.org/wiki/Shin_Megami_Tensei:_Devil_Children
- psxdatacenter: https://psxdatacenter.com/games/J/S/SLPM-87040.html
- Patch posts/listings: links in §2
