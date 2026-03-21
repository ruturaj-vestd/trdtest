setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run:
	streamlit run app/streamlit_app.py

batch:
	python scripts/run_batch.py --limit 10

live:
	python scripts/run_live_monitor.py

test:
	pytest -q

digest:
	python scripts/send_digest.py

retrain:
	python scripts/retrain_policy.py

promote:
	python scripts/promote_candidate.py
