.PHONY: run_fastapi run_streamlit
include .env

run_fastapi:
	uvicorn selection.api.fast:app --host 0.0.0.0 --reload

run_streamlit:
	streamlit run selection/frontend/app.py

deploy:
	cat .env
	docker build -t ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:prod .
	docker push ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:prod
	gcloud run deploy --image ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:${IMAGE_TAG} --memory ${GCR_MEMORY} --region ${GCP_REGION}
