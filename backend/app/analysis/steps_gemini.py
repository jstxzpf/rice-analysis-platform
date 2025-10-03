
import google.generativeai as genai
from app.core.config import settings
import pathlib
import json
from PIL import Image

# Configure the Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_with_gemini(drone_image_path: str, side_image_05m_path: str, side_image_horizontal_path: str, side_image_vertical_path: str) -> dict:
    """
    Analyzes rice paddy images using the Gemini Pro Vision model.
    """
    print("Starting analysis with Gemini Pro Vision...")

    try:
        # Model initialization
        model = genai.GenerativeModel('gemini-pro-vision')

        # Load images
        drone_image = Image.open(drone_image_path)
        side_image_05m = Image.open(side_image_05m_path)
        side_image_horizontal = Image.open(side_image_horizontal_path)
        side_image_vertical = Image.open(side_image_vertical_path)

        prompt = """
        You are an expert agricultural analyst specializing in rice cultivation.
        Analyze the following FOUR images of a rice paddy:
        1. A top-down drone view (Image 1).
        2. A 3-meter horizontal side view of the plants (Image 2).
        3. A 3-meter vertical side view of the plants (Image 3).
        4. A 0.5m close-up side view of a plant (Image 4).

        Your primary goal is to calculate key density metrics. Your response MUST be a single JSON object with two keys: "analysis" and "metrics".

        1.  **Analysis Key**:
            -   `description`: A detailed text analysis of the rice's growth status.
            -   `suggestions`: Actionable farming advice.

        2.  **Metrics Key**: Provide your best estimate for the following values.
            *   **Spacing Analysis (Crucial)**:
                -   `estimated_row_spacing_cm` (Float): From the horizontal view (Image 2), estimate the average distance between plant rows in centimeters.
                -   `estimated_plant_spacing_cm` (Float): From the vertical view (Image 3), estimate the average distance between individual plants/hills in the same row in centimeters.
            *   **Density Calculations**:
                -   `seedlings_per_mu` (Integer): Based on your estimated row and plant spacing, calculate the approximate number of seedlings per mu (亩). 1 mu = 666.67 square meters. The formula is `(666.67 * 10000) / (row_spacing_cm * plant_spacing_cm)`.
                -   `panicles_per_mu` (Integer): First, count the number of panicles in a 1-meter length from the horizontal view (Image 2) to get `panicle_count_in_1m_sample`. Then, use your estimated row spacing to calculate panicles per mu. The formula is `panicle_count_in_1m_sample * (666.67 * 100 / estimated_row_spacing_cm)`.
            *   **General Metrics**:
                -   `pest_risk`: (String) "Low", "Moderate", "High", or "Visible Evidence".
                -   `leaf_color_health`: (String) "Healthy Green", "Yellowish", "Dark Green", "Uneven".
                -   `lodging_status`: (String) "None", "Slight", "Moderate", "Severe".
                -   `estimated_leaf_age`: (Float) Average leaf age of the main stem.
                -   `estimated_tillers_per_plant`: (Float) Average number of tillers per plant/hill.


        Example of a valid JSON response:
        {
          "analysis": {
            "description": "The rice plants show uniform growth. The horizontal and vertical views allow for an accurate assessment of plant spacing.",
            "suggestions": "Maintain current irrigation and fertilization schedules. The plant density is optimal."
          },
          "metrics": {
            "estimated_row_spacing_cm": 25.0,
            "estimated_plant_spacing_cm": 15.0,
            "seedlings_per_mu": 17778,
            "panicles_per_mu": 450000,
            "pest_risk": "Low",
            "leaf_color_health": "Healthy Green",
            "lodging_status": "None",
            "estimated_leaf_age": 12.5,
            "estimated_tillers_per_plant": 22.0
          }
        }
        """

        # Generate content
        response = model.generate_content([prompt, drone_image, side_image_horizontal, side_image_vertical, side_image_05m])

        # Clean and parse the JSON response
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        result_json = json.loads(cleaned_response_text)

        analysis = result_json.get("analysis", {})
        metrics = result_json.get("metrics", {})

        # Prepare the dictionary for database insertion
        # The Gemini model is now expected to calculate these values directly.
        gemini_results = {
            "gemini_analysis_text": analysis.get("description"),
            "gemini_suggestions": analysis.get("suggestions"),
            "pest_risk": metrics.get("pest_risk"),
            "leaf_color_health": metrics.get("leaf_color_health"),
            "lodging_status": metrics.get("lodging_status"),
            "estimated_leaf_age": metrics.get("estimated_leaf_age"),
            "estimated_tillers_per_plant": metrics.get("estimated_tillers_per_plant"),
            "panicles_per_mu": metrics.get("panicles_per_mu"),
            # Add new fields, even if they are None
            "seedlings_per_mu": metrics.get("seedlings_per_mu"),
            "estimated_row_spacing_cm": metrics.get("estimated_row_spacing_cm"),
            "estimated_plant_spacing_cm": metrics.get("estimated_plant_spacing_cm"),
        }
        
        print("Gemini analysis completed successfully.")
        return gemini_results

    except Exception as e:
        print(f"An error occurred during Gemini analysis: {e}")
        # Return a dictionary with error information
        return {
            "gemini_analysis_text": f"AI analysis failed: {e}",
            "gemini_suggestions": "Could not generate suggestions due to an error.",
            "pest_risk": "Unknown",
            "leaf_color_health": "Unknown",
            "lodging_status": "Unknown",
        }

