from app.worker.celery_app import celery_app
from app.analysis.main_processor import process_photo_group

@celery_app.task(name="tasks.run_analysis", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 300})
def run_analysis(photo_group_id: int):
    """
    Celery task to run the full image analysis pipeline for a photo group.
    This task will automatically retry on failure.
    """
    process_photo_group(photo_group_id)
    return {"status": "complete", "photo_group_id": photo_group_id}
