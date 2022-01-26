#!/usr/bin/env bash
# this script list all released airflow images, currently does not
# ensure the images are supported on the platform version in question
# adding some filtering mechanism in the future may be desirable
airflow_image_tags=$(curl -s https://quay.io/v1/repositories/astronomer/ap-airflow/tags|jq 'keys[]' -r|grep -v latest)
while IFS= read -r src_tag; do
  echo "quay.io/astronomer/ap-airflow:${src_tag}"
done <<< "$airflow_image_tags"
