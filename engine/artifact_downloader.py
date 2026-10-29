import urllib.request
import json
import zipfile
import io
import os

class ArtifactSiphon:
    def __init__(self, repo="achadar839-creator/LegendCoderAI", download_dir="downloads"):
        self.repo = repo
        self.download_dir = download_dir
        self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self.headers = {"User-Agent": "InferSiphon/1.0"}
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
        os.makedirs(self.download_dir, exist_ok=True)

    def download_latest_apk(self, run_id):
        url = f"https://api.github.com/repos/{self.repo}/actions/runs/{run_id}/artifacts"
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                artifacts = data.get("artifacts", [])
                if not artifacts:
                    print("⚠️ कोई आर्टिफैक्ट नहीं मिला।")
                    return None
                
                # पहला APK आर्टीफैक्ट चुनना
                target = artifacts[0]
                download_url = target["archive_download_url"]
                print(f"📦 [Siphon] APK ज़िप डाउनलोड कर रहा है: {target['name']}...")

            # ज़िप फ़ाइल स्ट्रीम और अंदर से .apk निकालना
            down_req = urllib.request.Request(download_url, headers=self.headers)
            with urllib.request.urlopen(down_req) as d_resp:
                z = zipfile.ZipFile(io.BytesIO(d_resp.read()))
                for filename in z.namelist():
                    if filename.endswith(".apk"):
                        out_path = os.path.join(self.download_dir, os.path.basename(filename))
                        with open(out_path, "wb") as f:
                            f.write(z.read(filename))
                        print(f"✅ [Siphon] APK सुरक्षित सेव हो गया: {out_path}")
                        return out_path
        except Exception as e:
            print(f"❌ APK डाउनलोड में दिक्कत: {e}")
            return None
