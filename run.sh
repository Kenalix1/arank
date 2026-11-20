#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "Запуск реестра разрядов на Streamlit..."
streamlit run app.py
