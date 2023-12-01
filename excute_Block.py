from __future__ import annotations
import gradio as gr
from gradio.themes.base import Base
from gradio.themes.utils import colors, fonts, sizes
from typing import Iterable
import pymssql
import pandas as pd
import matplotlib.pyplot as plt


class Seafoam(Base):
    def __init__(
        self,
        *,
        primary_hue: colors.Color | str = colors.emerald,
        secondary_hue: colors.Color | str = colors.blue,
        neutral_hue: colors.Color | str = colors.blue,
        spacing_size: sizes.Size | str = sizes.spacing_md,
        radius_size: sizes.Size | str = sizes.radius_md,
        text_size: sizes.Size | str = sizes.text_lg,
        font: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("Quicksand"),
            "ui-sans-serif",
            "sans-serif",
        ),
        font_mono: fonts.Font
        | str
        | Iterable[fonts.Font | str] = (
            fonts.GoogleFont("IBM Plex Mono"),
            "ui-monospace",
            "monospace",
        ),
    ):
        super().__init__(
            primary_hue=primary_hue,
            secondary_hue=secondary_hue,
            neutral_hue=neutral_hue,
            spacing_size=spacing_size,
            radius_size=radius_size,
            text_size=text_size,
            font=font,
            font_mono=font_mono,
        )
        super().set(
            body_background_fill="repeating-linear-gradient(45deg, *primary_200, *primary_200 10px, *primary_50 10px, "
                                 "*primary_50 20px)",
            # body_background_fill="repeating-linear-gradient(45deg, *primary_200, *primary_200 10px, "
            #                      "*primary_200 10px, *primary_200 20px)",
            body_background_fill_dark="repeating-linear-gradient(45deg, *primary_800, *primary_800 10px, "
                                      "*primary_900 10px, *primary_900 20px)",
            button_primary_background_fill="linear-gradient(90deg, *primary_300, *secondary_400)",
            button_primary_background_fill_hover="linear-gradient(90deg, *primary_200, *secondary_300)",
            button_primary_text_color="white",
            button_primary_background_fill_dark="linear-gradient(90deg, *primary_600, *secondary_800)",
            slider_color="*secondary_300",
            slider_color_dark="*secondary_600",
            block_title_text_weight="600",
            block_border_width="3px",
            block_shadow="*shadow_drop_lg",
            button_shadow="*shadow_drop_lg",
            button_large_padding="32px",
        )


def search_value():
    all_machine = ['KQ01', 'KQ02', 'KQ03', 'KQ04', 'KQ05', 'KQ06', 'KQ07', 'KQ08']

    data_dict = {}

    for i in range(len(all_machine)):
        connection = pymssql.connect(
            host="10.3.96.168",
            user="N000184123",
            password="N000184123@npc",
            database="3033"
        )
        cursor = connection.cursor()

        table_name = 'kq_health'
        search_query = f'''
                SELECT 時間, 健康度
                FROM {table_name}
                WHERE 混合機名 = '{all_machine[i]}'
            '''
        cursor.execute(search_query)
        results = cursor.fetchall()
        connection.close()

        columns = ['時間', '健康度']

        pd_result = pd.DataFrame(results, columns=columns)

        data_dict[all_machine[i]] = pd_result

    return data_dict


def make_kq_plot(kq_selection):
    data = search_value()
    plt.plot(data[kq_selection]['時間'], data[kq_selection]['健康度'])
    plt.title('Health Trend')
    plt.xlabel('Time')
    plt.ylabel('Health')
    plt.grid(True)
    plt.tight_layout()
    return plt


def make_all_kq_plot():
    all_data = search_value()
    plt.plot(all_data['KQ01']['時間'], all_data['KQ01']['健康度'], label='KQ1')
    plt.plot(all_data['KQ02']['時間'], all_data['KQ02']['健康度'], label='KQ2')
    plt.plot(all_data['KQ03']['時間'], all_data['KQ03']['健康度'], label='KQ3')
    plt.plot(all_data['KQ04']['時間'], all_data['KQ04']['健康度'], label='KQ4')
    plt.plot(all_data['KQ05']['時間'], all_data['KQ05']['健康度'], label='KQ5')
    plt.plot(all_data['KQ06']['時間'], all_data['KQ06']['健康度'], label='KQ6')
    plt.plot(all_data['KQ07']['時間'], all_data['KQ07']['健康度'], label='KQ7')
    plt.plot(all_data['KQ08']['時間'], all_data['KQ08']['健康度'], label='KQ8')
    plt.title('ALL KQ Health Trend')
    plt.xlabel('Time')
    plt.ylabel('Health')
    plt.legend(bbox_to_anchor=(1.13, 0.5), loc='right')
    plt_image = plt.gcf()
    return plt_image


seafoam = Seafoam()

with gr.Blocks(theme=seafoam) as kq_webpage:
    with gr.Row():
        with gr.Column():
            gr.Markdown("# 南亞塑膠嘉義一廠混合健康度")
            gr.Markdown('## 開發者: 嘉義一廠 賴烱庭 (N000184910)')
        with gr.Column():
            kq_selection = gr.Radio(label="請點選監視的KQ機台",
                                    choices=['KQ01', 'KQ02', 'KQ03', 'KQ04', "KQ05", "KQ06", 'KQ07', 'KQ08'])
    with gr.Row():
        with gr.Column():
            plot = gr.Plot(label="健康8台趨勢圖")
        with gr.Column():
            kq_plot = gr.Plot(label="健康趨勢圖")

    kq_selection.change(make_kq_plot, inputs=kq_selection, outputs=[kq_plot])
    kq_webpage.load(make_all_kq_plot, None, outputs=[plot])
    # kq_webpage.load(make_kq_plot, inputs=[kq_selection], outputs=[kq_plot])


if __name__ == "__main__":
    kq_webpage.launch(server_name='10.114.70.170',
                      server_port=99)

