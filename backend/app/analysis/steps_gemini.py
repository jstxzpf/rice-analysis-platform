
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
        2. A horizontal side view of the plants (Image 2).
        3. A vertical side view of the plants, which includes a 1x2 meter board for scale (Image 3).
        4. A 0.5m close-up side view of a plant (Image 4).

        Based on these images, provide a comprehensive analysis. Your response MUST be a single JSON object with two keys: "analysis" and "metrics".

        1. The "analysis" key should contain an object with two string values:
           - "description": A detailed text analysis of the rice's growth status. Integrate insights from all four views. Use the close-up view (Image 4) to comment on fine details like leaf texture, dew, or potential early-stage issues.
           - "suggestions": Actionable farming advice based on your analysis.

        2. The "metrics" key should contain an object with your best estimate for the following values:
           - "pest_risk": (String) Use the close-up view (Image 4) to look for subtle signs like insect eggs, small spots, or discoloration to refine this risk. "Low", "Moderate", "High", or "Visible Evidence".
           - "leaf_color_health": (String) "Healthy Green", "Yellowish", "Dark Green", "Uneven".
           - "lodging_status": (String) Assess the degree of plant lodging from the vertical view (Image 3). "None", "Slight", "Moderate", "Severe".
           - "estimated_leaf_age": (Float) Use the close-up view (Image 4) to get a more accurate estimate of the average leaf age of the main stem.
           - "estimated_tillers_per_plant": (Float) Use the close-up view (Image 4) to refine your estimate of the average number of tillers per plant/hill.
           - "panicle_count_in_sample": (Integer) From the vertical view (Image 3), carefully count the number of rice panicles visible in the 2 square meter area in front of the 1x2m board.

        Example of a valid JSON response:
        {
          "analysis": {
            "description": "...The close-up view reveals healthy leaf texture with no visible signs of fungal infection...",
            "suggestions": "...The high-resolution view confirms no immediate need for fungicides..."
          },
          "metrics": {
            "pest_risk": "Low",
            "leaf_color_health": "Healthy Green",
            "lodging_status": "None",
            "estimated_leaf_age": 12.5,
            "estimated_tillers_per_plant": 22.0,
            "panicle_count_in_sample": 125
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

        # Calculate panicles per mu from the sample count
        panicles_per_mu = 0
        panicle_count_in_sample = metrics.get("panicle_count_in_sample")
        if isinstance(panicle_count_in_sample, int):
            # Extrapolate from 2 sq. meters to 1 mu (666.67 sq. meters)
            panicles_per_mu = round((panicle_count_in_sample / 2) * 666.67)

        # Prepare the dictionary for database insertion
        gemini_results = {
            "gemini_analysis_text": analysis.get("description"),
            "gemini_suggestions": analysis.get("suggestions"),
            "pest_risk": metrics.get("pest_risk"),
            "leaf_color_health": metrics.get("leaf_color_health"),
            "lodging_status": metrics.get("lodging_status"),
            "estimated_leaf_age": metrics.get("estimated_leaf_age"),
            "estimated_tillers_per_plant": metrics.get("estimated_tillers_per_plant"),
            "panicles_per_mu": panicles_per_mu,
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

