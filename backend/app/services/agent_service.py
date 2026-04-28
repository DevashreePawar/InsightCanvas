from app.services.chart_service import generate_chart, recommend_chart
from app.services.csv_service import get_dataset, get_dataset_metadata
from app.services.profile_service import profile_dataset
from app.services.rag_service import retrieve_dataset_context


def interpret_dataset_question(dataset_id: str, question: str) -> dict:
    df = get_dataset(dataset_id)
    metadata = get_dataset_metadata(dataset_id)
    profile = profile_dataset(df, metadata)
    context = retrieve_dataset_context(dataset_id, question)
    return recommend_chart(question, profile, None, context)


def analyze_dataset_question(dataset_id: str, question: str) -> dict:
    df = get_dataset(dataset_id)
    metadata = get_dataset_metadata(dataset_id)
    context = retrieve_dataset_context(dataset_id, question)
    return generate_chart(df, question, metadata, context)
