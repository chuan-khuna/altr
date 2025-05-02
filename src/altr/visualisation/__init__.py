import os
import matplotlib.pyplot as plt
import importlib
import seaborn as sns

STYLE_DIR = os.path.join(os.path.dirname(__file__), "styles")


def _list_styles() -> list[str]:
    """
    List available styles
    """

    files = os.listdir(STYLE_DIR)
    style_names = list(map(lambda filename: filename.split(".mplstyle")[0], files))

    return style_names


available_styles = _list_styles()


def set_style(name: str) -> None:
    """
    Set matplotlib style


    Args:
        name (str): name of the style
    """

    if name not in available_styles:
        # fallback to matplotlib style
        plt.style.use(name)

    file = f"{name}.mplstyle"
    plt.style.use(os.path.join(STYLE_DIR, file))


def set_seaborn_palette(name: str) -> None:
    # dynamically import the style from palettes
    module = importlib.import_module(f"altr.visualisation.palettes.{name}")

    if name == 'ft':
        colors = getattr(module, "vis_colors", None).values()
    else:
        colors = getattr(module, "main_colors", None).values()

    sns.set_palette(colors)
