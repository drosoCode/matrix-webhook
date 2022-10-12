# Matrix Webhook Gateway

Features:
  - Configuration in yaml, no database
  - E2E Encryption Support (with emoji verification)
  - Multi-User support
  - Extensible with custom formatters
  - Built-in support for Discord, Graylog, Sonarqube, Github, Grafana

## Usage

Using the `config.sample.yaml` file, create your configuration file.

Then use the provided docker-compose file, configure your volumes and your reverse proxy (traefik in the example) and run `docker-compose up -d`.
