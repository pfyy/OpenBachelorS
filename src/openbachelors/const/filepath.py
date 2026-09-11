from .region import GAME_REGION, GameRegion

CONFIG_JSON = "conf/config.json"
VERSION_JSON_CN = "conf/version.json"
VERSION_JSON_EN = "conf/version_en.json"

match GAME_REGION:
    case GameRegion.GAME_REGION_CN:
        VERSION_JSON = VERSION_JSON_CN
    case GameRegion.GAME_REGION_EN:
        VERSION_JSON = VERSION_JSON_EN

VERSION_WINDOWS_JSON_CN = "conf/version_windows.json"
VERSION_WINDOWS_JSON_EN = "conf/version_en_windows.json"

match GAME_REGION:
    case GameRegion.GAME_REGION_CN:
        VERSION_WINDOWS_JSON = VERSION_WINDOWS_JSON_CN
    case GameRegion.GAME_REGION_EN:
        VERSION_WINDOWS_JSON = VERSION_WINDOWS_JSON_EN


ASSIST_JSON = "conf/assist.json"
SQUAD_JSON = "conf/squad.json"

TMPL_JSON = "data/tmpl.json"
RLV2_TMPL_JSON = "data/rlv2_tmpl.json"
SANDBOX_TMPL_JSON = "data/sandbox_tmpl.json"
CRISIS_V2_TMPL_JSON = "data/crisisV2_tmpl.json"
MAIL_JSON = "data/mail.json"
MESSAGE_JSON = "data/message.json"
GACHA_POOL_JSON = "data/gacha_pool.json"
RLV2_DATA = "data/rlv2_data.json"
GACHA_DATA = "data/gacha_data.json"
CRISIS_V2_DATA_DIRPATH = "data/crisisV2/"

SAV_DELTA_JSON = "sav/delta.json"
SAV_PENDING_DELTA_JSON = "sav/pending_delta.json"

MULTI_USER_SAV_DIRPATH = "multi_sav/"

REPLAY_DIRPATH = "sav/replay/"

MULTI_REPLAY_DIRPATH = "multi_sav/replay/"

EXTRA_SAVE_FILEPATH = "sav/extra.json"

MULTI_EXTRA_SAVE_DIRPATH = "multi_sav/"

TMP_DIRPATH = "tmp/"

ASSET_DIRPATH = "asset/"

MOD_DIRPATH = "mod/"
MOD_WINDOWS_DIRPATH = "mod_windows/"

GAME_LINK_FILEPATH = "link/game.txt"
PC_GAME_LINK_FILEPATH = "link/pc_game.txt"
PC_GAME_EN_LINK_FILEPATH = "link/pc_game_en.txt"
MUMU_LINK_FILEPATH = "link/mumu12.txt"
MUMU_15_LINK_FILEPATH = "link/mumu15.txt"
LD_LINK_FILEPATH = "link/ld14.txt"

RES_LOCK_FILEPATH = "res_lock"

RES_EXCEL_DIRPATH_CN = "res/excel/"
RES_EXCEL_DIRPATH_EN = "res_en/excel/"


match GAME_REGION:
    case GameRegion.GAME_REGION_CN:
        RES_EXCEL_DIRPATH = RES_EXCEL_DIRPATH_CN
    case GameRegion.GAME_REGION_EN:
        RES_EXCEL_DIRPATH = RES_EXCEL_DIRPATH_EN


SKIN_TABLE = RES_EXCEL_DIRPATH + "skin_table.json"
CHARWORD_TABLE = RES_EXCEL_DIRPATH + "charword_table.json"
UNIEQUIP_TABLE = RES_EXCEL_DIRPATH + "uniequip_table.json"
CHARACTER_TABLE = RES_EXCEL_DIRPATH + "character_table.json"
STORY_TABLE = RES_EXCEL_DIRPATH + "story_table.json"
STAGE_TABLE = RES_EXCEL_DIRPATH + "stage_table.json"
HANDBOOK_INFO_TABLE = RES_EXCEL_DIRPATH + "handbook_info_table.json"
RETRO_TABLE = RES_EXCEL_DIRPATH + "retro_table.json"
DISPLAY_META_TABLE = RES_EXCEL_DIRPATH + "display_meta_table.json"
MEDAL_TABLE = RES_EXCEL_DIRPATH + "medal_table.json"
STORY_REVIEW_TABLE = RES_EXCEL_DIRPATH + "story_review_table.json"
STORY_REVIEW_META_TABLE = RES_EXCEL_DIRPATH + "story_review_meta_table.json"
ENEMY_HANDBOOK_TABLE = RES_EXCEL_DIRPATH + "enemy_handbook_table.json"
ACTIVITY_TABLE = RES_EXCEL_DIRPATH + "activity_table.json"
CHAR_PATCH_TABLE = RES_EXCEL_DIRPATH + "char_patch_table.json"
CLIMB_TOWER_TABLE = RES_EXCEL_DIRPATH + "climb_tower_table.json"
BUILDING_DATA = RES_EXCEL_DIRPATH + "building_data.json"
SANDBOX_PERM_TABLE = RES_EXCEL_DIRPATH + "sandbox_perm_table.json"
ROGUELIKE_TOPIC_TABLE = RES_EXCEL_DIRPATH + "roguelike_topic_table.json"
GACHA_TABLE = RES_EXCEL_DIRPATH + "gacha_table.json"
CRISIS_V2_TABLE = RES_EXCEL_DIRPATH + "crisis_v2_table.json"
CAMPAIGN_TABLE = RES_EXCEL_DIRPATH + "campaign_table.json"
CHAR_META_TABLE = RES_EXCEL_DIRPATH + "char_meta_table.json"
