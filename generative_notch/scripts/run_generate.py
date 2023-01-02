import logging
from datetime import datetime
from generative_notch import init_logger, get_config
from generative_notch.rarity_table import RarityTable
from generative_notch.combination_assembler import CombinationAssembler
from generative_notch.render import Renderer

init_logger()
cfg = get_config()

logging.warning(f"Starting generation of NFT batch: {cfg['batch_name']}")
start_time = datetime.now()

rarity_table = RarityTable.from_google_sheets(
    credentials_filename=cfg['google_sheets']['credentials'],
    sheet_filename=cfg['google_sheets']['sheet'],
    worksheet_name=cfg['google_sheets']['worksheet']
)

n = input(f'Possible combinations: {rarity_table.max_combinations}, how many generate?: ')
combinations = rarity_table.generate_combinations(int(n) if n else -1)
rarity_table.save(
    filename=f"{cfg['google_sheets']['sheet']}_{cfg['google_sheets']['worksheet']}",
    directory=cfg['output_dir']
)

assembler = CombinationAssembler(template_project_filepath=cfg['dfx_template_file'])
render_list = assembler.assemble(
    combinations=combinations,
    out_project_dir=cfg['dfx_intermediate_dir'],
    out_project_name=cfg['batch_name'],
    out_video_dir=cfg['output_dir']
)

renderer = Renderer(render_list)
renderer.run()

logging.info(f"Done generating NFT batch, took {(datetime.now() - start_time).seconds} seconds")
