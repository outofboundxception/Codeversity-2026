from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import traceback

from schemas.api_schemas import PredictionRequest, PredictionResponse, PredictionData, MetadataInfo, ErrorInfo
from utils.helpers import decode_base64_image, preprocess_frame
from preprocessing.landmark_detector import HandLandmarkDetector
from models.gesture_model import get_model

landmark_detector = None
gesture_model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global landmark_detector, gesture_model
    print("🚀 Starting ISL Translator API...")
    landmark_detector = HandLandmarkDetector(max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    gesture_model = get_model()
    print("✅ All components loaded")
    yield
    print("🛑 Shutting down...")
    landmark_detector.close()

app = FastAPI(title="ISL Translator API", description="Real-time Indian Sign Language to Speech Translation", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"status": "running", "service": "ISL Translator API", "version": "1.0.0"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "components": {
            "landmark_detector": "ready" if landmark_detector else "not loaded",
            "gesture_model": "ready" if gesture_model else "not loaded"
        },
        "model_info": gesture_model.get_info() if gesture_model else None
    }

@app.post("/api/predict", response_model=PredictionResponse)
async def predict_gesture(request: PredictionRequest):
    start_time = time.time()
    try:
        try:
            frame = decode_base64_image(request.frame)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid frame data: {str(e)}")
        
        processed_frame = preprocess_frame(frame)
        landmarks = landmark_detector.detect(processed_frame)
        
        if landmarks is None:
            processing_time = round((time.time() - start_time) * 1000, 2)
            return PredictionResponse(
                success=False, frame_id=request.frame_id, prediction=None,
                metadata=MetadataInfo(landmarks_detected=False, processing_time_ms=processing_time),
                error=ErrorInfo(code="NO_HAND_DETECTED", message="No hand found in frame. Please show your hand clearly.")
            )
        
        gesture_text, confidence = gesture_model.predict(landmarks)
        confidence_threshold = 0.5
        
        if confidence < confidence_threshold:
            processing_time = round((time.time() - start_time) * 1000, 2)
            return PredictionResponse(
                success=True, frame_id=request.frame_id,
                prediction=PredictionData(text=None, confidence=confidence, gesture_id=None),
                metadata=MetadataInfo(landmarks_detected=True, processing_time_ms=processing_time, warning=f"Confidence {confidence} below threshold {confidence_threshold}")
            )
        
        processing_time = round((time.time() - start_time) * 1000, 2)
        return PredictionResponse(
            success=True, frame_id=request.frame_id,
            prediction=PredictionData(text=gesture_text, confidence=confidence, gesture_id=f"ISL_{gesture_text.upper().replace(' ', '_')}"),
            metadata=MetadataInfo(landmarks_detected=True, processing_time_ms=processing_time)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error processing frame {request.frame_id}:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail={"error": "Internal server error", "message": str(e), "frame_id": request.frame_id})

@app.get("/api/gestures")
def list_gestures():
    return {"gestures": gesture_model.gestures if gesture_model else [], "count": len(gesture_model.gestures) if gesture_model else 0}
