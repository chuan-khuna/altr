import os
import matplotlib.pyplot as plt

__STYLE_CONFIG_FOLDER = "styles_conf"
STYLE_DIR = os.path.join(os.path.dirname(__file__), __STYLE_CONFIG_FOLDER)


def _list_styles() -> list[str]:
    """
    List available styles
    """
    files = os.listdir(STYLE_DIR)
    style_names = [filename.split(".mplstyle")[0] for filename in files]
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


__all__ = ["set_style", "available_styles"]
