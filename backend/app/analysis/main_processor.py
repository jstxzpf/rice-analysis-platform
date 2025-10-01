from sqlalchemy.orm import Session
from app.db import models, base
from app.crud import crud_analysis_result
from . import steps_analyze
from . import steps_gemini

def process_photo_group(photo_group_id: int):
    db: Session = next(base.get_db())
    try:
        photo_group = db.query(models.PhotoGroup).filter(models.PhotoGroup.id == photo_group_id).first()
        if not photo_group:
            print(f"Error: PhotoGroup {photo_group_id} not found.")
            return

        # Update status to PROCESSING
        photo_group.analysis_status = models.AnalysisStatusEnum.PROCESSING
        db.commit()

        # --- Run Analysis Steps ---
        coverage_results = steps_analyze.analyze_drone_view(photo_group.drone_photo_path)
        height_results = steps_analyze.analyze_side_view_height(photo_group.side_photo_3m_vertical_path)
        advanced_side_view_results = steps_analyze.analyze_side_view_advanced(
            horizontal_path=photo_group.side_photo_3m_horizontal_path,
            vertical_path=photo_group.side_photo_3m_vertical_path
        )

        # --- Run Gemini AI Analysis ---
        gemini_results = steps_gemini.analyze_with_gemini(
            drone_image_path=photo_group.drone_photo_path,
            side_image_05m_path=photo_group.side_photo_05m_path,
            side_image_horizontal_path=photo_group.side_photo_3m_horizontal_path,
            side_image_vertical_path=photo_group.side_photo_3m_vertical_path
        )

        # --- Create Result Record ---
        analysis_data = {
            **coverage_results,
            **height_results,
            **advanced_side_view_results,
            **gemini_results,
        }
        crud_analysis_result.create_analysis_result(db, photo_group_id, analysis_data)

        # Update status to COMPLETED
        photo_group.analysis_status = models.AnalysisStatusEnum.COMPLETED
        db.commit()
        print(f"Analysis for PhotoGroup {photo_group_id} completed successfully.")

    except Exception as e:
        db.rollback()
        photo_group = db.query(models.PhotoGroup).filter(models.PhotoGroup.id == photo_group_id).first()
        if photo_group:
            photo_group.analysis_status = models.AnalysisStatusEnum.FAILED
            db.commit()
        print(f"An error occurred during analysis for PhotoGroup {photo_group_id}: {e}")
    finally:
        db.close()
