import os
import importlib
import seaborn as sns


__PALETTE_CONFIG_FODLER = "palettes_conf"


def _list_palettes() -> list[str]:
    """
    List available palettes
    """
    files = os.listdir(os.path.join(os.path.dirname(__file__), __PALETTE_CONFIG_FODLER))
    palette_names = [filename.split(".py")[0] for filename in files]
    palette_names = [name for name in palette_names if not name.startswith("_")]
    return palette_names


available_palettes = _list_palettes()


def set_seaborn_palette(name: str, scheme: str = "main_colors") -> None:
    # dynamically import the style from palettes
    module = importlib.import_module(f"altr.visualisation.{__PALETTE_CONFIG_FODLER}.{name}")
    colors = getattr(module, scheme, None)
    if colors is None:
        raise AttributeError(f"Palette '{name}' does not have a scheme '{scheme}'")
    sns.set_palette(list(colors.values()))


__all__ = ["set_seaborn_palette", "available_palettes"]
