import argparse
import json
import os
import sys
from typing import Dict, Any, List
from google.cloud import vision
from google.cloud.vision_v1 import types as vision_types

#!/usr/bin/env python3


def _warn_creds():
    if not os.getenv("GOOGLE_VISON_CRED"):
        sys.stderr.write("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. Set it to your service account JSON key path.\n")


def _make_image(resource: str) -> vision.Image:
    if resource.startswith("gs://"):
        return vision.Image(source=vision.ImageSource(image_uri=resource))
    # Local file
    with open(resource, "rb") as f:
        content = f.read()
    return vision.Image(content=content)


def _handle_error(resp, feature_name: str):
    if resp.error and resp.error.message:
        raise RuntimeError(f"{feature_name} error: {resp.error.message}")


def detect_labels(client: vision.ImageAnnotatorClient, image: vision.Image) -> List[Dict[str, Any]]:
    resp = client.label_detection(image=image)
    _handle_error(resp, "label_detection")
    out = []
    for l in resp.label_annotations:
        out.append({
            "description": l.description,
            "score": round(float(l.score), 4),
            "topicality": round(float(getattr(l, "topicality", 0.0)), 4),
        })
    return out


def detect_text(client: vision.ImageAnnotatorClient, image: vision.Image) -> Dict[str, Any]:
    resp = client.text_detection(image=image)
    _handle_error(resp, "text_detection")
    result = {"full_text": "", "locale": "", "blocks": []}
    if resp.full_text_annotation and resp.full_text_annotation.text:
        result["full_text"] = resp.full_text_annotation.text
        # Locale best effort (may be empty)
        try:
            result["locale"] = resp.text_annotations[0].locale if resp.text_annotations else ""
        except Exception:
            result["locale"] = ""
        # Return minimal block info
        for page in resp.full_text_annotation.pages:
            for block in page.blocks:
                block_text = "".join(
                    "".join(sym.text for sym in word.symbols) + " "
                    for para in block.paragraphs
                    for word in para.words
                ).strip()
                vertices = [{"x": v.x, "y": v.y} for v in block.bounding_box.vertices]
                result["blocks"].append({"text": block_text, "vertices": vertices})
    else:
        # Fallback to first text_annotation description if present
        if resp.text_annotations:
            result["full_text"] = resp.text_annotations[0].description
            result["locale"] = resp.text_annotations[0].locale
    return result


def detect_objects(client: vision.ImageAnnotatorClient, image: vision.Image) -> List[Dict[str, Any]]:
    resp = client.object_localization(image=image)
    _handle_error(resp, "object_localization")
    out = []
    for obj in resp.localized_object_annotations:
        vertices = [{"x": v.x, "y": v.y} for v in obj.bounding_poly.normalized_vertices]
        out.append({
            "name": obj.name,
            "score": round(float(obj.score), 4),
            "normalized_vertices": vertices,
        })
    return out


def detect_web(client: vision.ImageAnnotatorClient, image: vision.Image) -> Dict[str, Any]:
    resp = client.web_detection(image=image)
    _handle_error(resp, "web_detection")
    wd = resp.web_detection
    result = {
        "best_guess_labels": [l.label for l in (wd.best_guess_labels or [])],
        "web_entities": [{"description": e.description, "score": round(float(e.score), 4)} for e in (wd.web_entities or [])],
        "full_matching_images": [img.url for img in (wd.full_matching_images or [])],
        "partial_matching_images": [img.url for img in (wd.partial_matching_images or [])],
        "pages_with_matching_images": [p.url for p in (wd.pages_with_matching_images or [])],
    }
    return result


def detect_logos(client: vision.ImageAnnotatorClient, image: vision.Image) -> List[Dict[str, Any]]:
    resp = client.logo_detection(image=image)
    _handle_error(resp, "logo_detection")
    return [{"description": l.description, "score": round(float(l.score), 4)} for l in resp.logo_annotations]


def detect_landmarks(client: vision.ImageAnnotatorClient, image: vision.Image) -> List[Dict[str, Any]]:
    resp = client.landmark_detection(image=image)
    _handle_error(resp, "landmark_detection")
    out = []
    for lm in resp.landmark_annotations:
        locs = [{"lat": loc.lat_lng.latitude, "lng": loc.lat_lng.longitude} for loc in lm.locations]
        out.append({"description": lm.description, "score": round(float(lm.score), 4), "locations": locs})
    return out


def detect_safe_search(client: vision.ImageAnnotatorClient, image: vision.Image) -> Dict[str, Any]:
    resp = client.safe_search_detection(image=image)
    _handle_error(resp, "safe_search_detection")
    s = resp.safe_search_annotation
    def name(v: int) -> str:
        try:
            return vision_types.Likelihood(v).name
        except Exception:
            return str(v)
    return {
        "adult": name(s.adult),
        "spoof": name(s.spoof),
        "medical": name(s.medical),
        "violence": name(s.violence),
        "racy": name(s.racy),
    }


def detect_faces(client: vision.ImageAnnotatorClient, image: vision.Image) -> List[Dict[str, Any]]:
    resp = client.face_detection(image=image)
    _handle_error(resp, "face_detection")
    def name(v: int) -> str:
        try:
            return vision_types.Likelihood(v).name
        except Exception:
            return str(v)
    out = []
    for f in resp.face_annotations:
        verts = [{"x": v.x, "y": v.y} for v in f.bounding_poly.vertices]
        out.append({
            "detection_confidence": round(float(f.detection_confidence), 4),
            "joy": name(f.joy_likelihood),
            "sorrow": name(f.sorrow_likelihood),
            "anger": name(f.anger_likelihood),
            "surprise": name(f.surprise_likelihood),
            "under_exposed": name(f.under_exposed_likelihood),
            "blurred": name(f.blurred_likelihood),
            "headwear": name(f.headwear_likelihood),
            "bounding_poly": verts,
        })
    return out


FEATURES = {
    "label": detect_labels,
    "text": detect_text,
    "object": detect_objects,
    "web": detect_web,
    "logo": detect_logos,
    "landmark": detect_landmarks,
    "safe": detect_safe_search,
    "face": detect_faces,
}

ALL_FEATURES = list(FEATURES.keys())


def main():
    parser = argparse.ArgumentParser(description="Google Cloud Vision test application")
    parser.add_argument("image", help="Path to local image file or GCS URI (gs://bucket/object)")
    parser.add_argument(
        "--features",
        default="label,text",
        help=f"Comma-separated features to run. Options: {','.join(ALL_FEATURES)} or 'all'. Default: label,text",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    _warn_creds()

    feats = [f.strip().lower() for f in args.features.split(",")] if args.features else []
    if "all" in feats:
        feats = ALL_FEATURES
    # Validate
    unknown = [f for f in feats if f not in FEATURES]
    if unknown:
        sys.stderr.write(f"Unknown features: {', '.join(unknown)}\n")
        sys.exit(2)

    client = vision.ImageAnnotatorClient()
    image = _make_image(args.image)

    result: Dict[str, Any] = {"image": args.image, "results": {}}
    for f in feats:
        try:
            result["results"][f] = FEATURES[f](client, image)
        except Exception as e:
            result["results"][f] = {"error": str(e)}

    if args.pretty:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result, separators=(",", ":"), ensure_ascii=False))


if __name__ == "__main__":
    main()