from app.worker.celery_app import celery_app
from app.analysis.main_processor import process_photo_group

@celery_app.task(name="tasks.run_analysis")
def run_analysis(photo_group_id: int):
    """
    Celery task to run the full image analysis pipeline for a photo group.
    """
    process_photo_group(photo_group_id)
    return {"status": "complete", "photo_group_id": photo_group_id}
