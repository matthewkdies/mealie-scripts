# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Created initial bones of the `mealie-scripts` CLI:
  - `mealie-scripts recipes`:
    - `mealie-scripts recipes check-macros`: Adds high protein and high fiber tags to recipes based on recipes' nutrional information.
    - `mealie-scripts recipes check-quick`: Adds a quick tag to recipes based on recipes' total time attribute.
  - `mealie-scripts tags`:
    - `mealie-scripts tag list`: Lists all tags on the Mealie instance.
  - `mealie-scripts cache`:
    - `mealie-scripts cache list`: Lists the caches available, whether they exist, and their descriptions.
    - `mealie-scripts cache clear`: Clears one or all caches.
  - `mealie-scripts debug`:
    - `mealie-scripts debug show-config`: Shows the CLI's configuration from the settings.
    - `mealie-scripts debug test-connection`: Tests the CLI's connection to the configured Mealie instance.
  - Configuration of CLI from environment variables using `pydantic-settings`.
  - Connection to and interaction with Mealie instance via `httpx2`.
  - Cache definition for commands that run on all recipes.
