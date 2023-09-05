.PHONY: run_fastapi run_streamlit

run_fastapi:
	uvicorn selection.api.fast:app --host 0.0.0.0 --reload

run_streamlit:
	streamlit run selection/frontend/app.py
