# Roadmap

This document outlines the planned future development for the `mealie-scripts` CLI.

## Stability & Infrastructure

- [ ] **Implement unit tests**: Increase test coverage to ensure reliability of existing commands.
- [ ] **GitHub Actions**: Implement CI/CD pipeline to automate testing and package publishing.

## Documentation

- [ ] **Documentation**: Build and publish project documentation using Zensical and host it on GitHub Pages.

## Enhanced Functionality

- [ ] **Recipe caching**: Certain commands fetch the recipes every time, but others might not need to. Returning all recipes and saving them locally would be nice.
- [ ] **Ntfy.sh Support**: Add optional notification support to inform users of job status (e.g., successful recipe updates).
- [ ] **Expanded CLI Capabilities**: Add further features to help organize Mealie instances.
- [ ] **Recipe Portioning**: Many recipes come in serving sizes that are too large or small for your normal usage. I'd love to implement auto-scaling to set a default serving size, and then edit recipes (meaning ingredient quantities and the default number of servings) to fit this size. There's some complexity here though, many units don't necessarily scale well (e.g., "1 can of beans") and other types of recipes probably shouldn't be scaled (e.g., desserts).
- [ ] **Automated Meal Planning**: A bit of a stretch goal here, but I'd love to be able to automatically create meal plans with a certain amount of "health" based on the known recipes and tags.
