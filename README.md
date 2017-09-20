# docker-jinja-configurator

```yaml
version: "3.2"

services:
  my_service:
    image: my_service
    depends_on:
      - configs
    volumes:
      - type: volume
        source: my_service_config
        target: /etc/my_service/

  configs:
    image: bkhasanov/docker-jinja-configurator
    volumes:
      - type: bind
        source: ./configs/templates/
        target: /templates/
        read_only: true

      - type: bind
        source: ./configs/data/
        target: /data/
        read_only: true

      - type: volume
        source: my_service_config
        target: /output/my_service/etc/my_service

volumes:
  my_service_config:

```
