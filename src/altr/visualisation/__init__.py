import os
import matplotlib.pyplot as plt


STYLE_DIR = os.path.join(os.path.dirname(__file__), "styles")


def list_styles() -> list[str]:
    """
    List available styles
    """

    files = os.listdir(STYLE_DIR)
    style_names = list(map(lambda filename: filename.split(".mplstyle")[0], files))

    return style_names


def set_style(name: str) -> None:
    """
    Set matplotlib style


    Args:
        name (str): name of the style
    """

    available_styles = list_styles()
    if name not in available_styles:
        raise ValueError(f"Style {name} not found, available styles are: {available_styles}")

    file = f"{name}.mplstyle"
    plt.style.use(os.path.join(STYLE_DIR, file))
