import google.generativeai as genai

genai.configure(api_key="YOUR_GEMINI_KEY")

class GeminiAnalyzer:
    def analyze_frame(self, frame_path, prompt="Есть ли деструктивный контент?"):
        model = genai.GenerativeModel('gemini-pro-vision')
        img = genai.upload_file(frame_path)
        response = model.generate_content([prompt, img])
        return response.text
