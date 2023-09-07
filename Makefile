.PHONY: run_fastapi run_streamlit deploy
include .env

run_fastapi:
	uvicorn selection.api.fast:app --host 0.0.0.0 --reload

run_streamlit:
	streamlit run selection/frontend/app.py

deploy:
	cat .env
	docker build -t ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:${IMAGE_TAG} .
	docker push ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:${IMAGE_TAG}
	gcloud run deploy --image ${GCR_REGION}/${GCP_PROJECT}/${GCR_IMAGE}:${IMAGE_TAG} --memory ${GCR_MEMORY} --region ${GCP_REGION} --cpu ${GCP_CPUS:-8} --min-instances ${GCP_MIN_INSTANCES:-1}
