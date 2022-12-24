# Deploy latest image
docker tag nenekabot gcr.io/$GCP_PROJECT_ID/$PROJECT_IMAGE
docker push gcr.io/$GCP_PROJECT_ID/$PROJECT_IMAGE