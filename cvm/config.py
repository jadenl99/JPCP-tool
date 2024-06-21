from dynaconf import LazySettings

settings = LazySettings(
    settings_files=["configs/settings.yaml"],
    envvar_prefix=False,
    environments=True,
    load_dotenv=True,
)
