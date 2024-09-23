\*\* aws-otel-collector

    docker run --rm -p 4317:4317 -p 55680:55680 -p 8889:8888 \
      -e AWS_REGION=us-east-1 \
      -e AWS_PROFILE=default \
      -v ~/.aws:/home/aoc/.aws \
      -v /tmp:/data \
      -v "${PWD}/otel-collector.yaml":/otel-local-config.yaml \
      --name awscollector public.ecr.aws/aws-observability/aws-otel-collector:latest \
      --config otel-local-config.yaml;

\*\* opentelemetry-collector-contrib

docker run -p 4317:4317 -p 55679:55679 \
 -v $(pwd)/otel-collector.yaml:/etc/otelcol-contrib/config.yaml \
 -v /tmp:/data \
 otel/opentelemetry-collector-contrib:0.100.0
