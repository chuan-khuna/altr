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
    style_names = [filename.split(".mplstyle")[0] for filename in files]

    return style_names


def _list_palettes() -> list[str]:
    """
    List available palettes
    """

    files = os.listdir(os.path.join(os.path.dirname(__file__), "palettes"))
    palette_names = [filename.split(".py")[0] for filename in files]
    palette_names = [name for name in palette_names if not name.startswith("_")]

    return palette_names


available_styles = _list_styles()
available_palettes = _list_palettes()


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


def set_seaborn_palette(name: str, scheme: str = "main_colors") -> None:
    # dynamically import the style from palettes
    module = importlib.import_module(f"altr.visualisation.palettes.{name}")
    colors = getattr(module, scheme, None).values()

    sns.set_palette(colors)
