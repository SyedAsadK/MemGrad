def main(*args, **kwargs):
    from .cli import main as _cli_main
    return _cli_main(*args, **kwargs)

__all__ = ["main"]
