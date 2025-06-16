from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

app = Flask(__name__)

# Cấu hình session với retry
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)

# Hàm crawl điểm từ Vietnamnet
def Crawl_THPTQG(so_bao_danh):
    so_bao_danh = str(so_bao_danh).rjust(8, '0')
    URL = f"https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/2024/{so_bao_danh}.html"
    r = session.get(URL)
    if r.status_code != 404:
        soup = BeautifulSoup(r.content, 'html.parser')
        target = soup.find('div', attrs={'class': 'resultSearch__right'})
        if not target:
            return None
        table = target.find('tbody')
        if not table:
            return None
        rows = table.find_all('tr')

        html_result = f"<strong style='font-size: 18px;'>📌 Số báo danh:</strong> <span style='font-weight: bold;'>{so_bao_danh}</span><br><br>"
        html_result += """
        <table style="width: 100%; border-collapse: collapse; background: white; color: black; font-size: 16px;">
            <thead style="background-color: #f2f2f2;">
                <tr>
                    <th style="border: 1px solid #ccc; padding: 8px;">Môn</th>
                    <th style="border: 1px solid #ccc; padding: 8px;">Điểm</th>
                </tr>
            </thead>
            <tbody>
        """
        for row in rows:
            cols = [ele.text.strip() for ele in row.find_all('td')]
            if len(cols) >= 2:
                mon, diem = cols[0], cols[1]
                html_result += f"""
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">{mon}</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: center;">{diem}</td>
                    </tr>
                """
        html_result += "</tbody></table>"
        return html_result
    return None

# Route kiểm tra kết nối Vietnamnet
@app.route("/ping-vietnamnet")
def ping_vietnamnet():
    try:
        r = session.get("https://vietnamnet.vn/giao-duc/diem-thi", timeout=5)
        if r.status_code == 200:
            return jsonify({"ok": True})
        return jsonify({"ok": False, "status": r.status_code})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

# HTML giao diện
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Tra cứu điểm thi THPT 2025</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(to right, #a9825a, #6e4f33);
            font-family: 'Segoe UI', sans-serif;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: #fff;
            flex-direction: column;
        }
        .header {
            position: absolute;
            top: 20px;
            left: 20px;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            width: 90%;
            max-width: 500px;
            text-align: center;
        }
        h2 {
            margin-top: 0;
            font-size: 24px;
            color: #fff;
        }
        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            margin: 12px 0;
            border-radius: 8px;
            border: none;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            border-radius: 8px;
            background-color: #8b5e3c;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background-color: #734a2b;
        }
        #ketQua {
            margin-top: 20px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 8px;
            color: #000;
        }
        .footer {
            margin-top: 30px;
            font-size: 14px;
            color: #eee;
        }
    </style>
</head>
<body>
    <div class="header">
        <iframe src="https://drive.google.com/file/d/1M4HBeFyqFi8VyGxKGeKD-93ZD8bwXHOw/preview" width="120" height="90" allow="autoplay"></iframe>
    </div>

    <div class="container">
        <h2>🎓 Tra cứu điểm thi THPT Quốc Gia 2025</h2>
        <div id="serverStatus" style="margin-bottom: 12px; font-weight: bold;"></div>
        <form id="formTraCuu">
            <label for="sbd">Nhập số báo danh:</label>
            <input type="text" id="sbd" required placeholder="VD: 63003654">
            <button type="submit">Tra cứu</button>
        </form>
        <div id="ketQua">Kết quả sẽ hiển thị ở đây...</div>
    </div>

    <div class="footer">© 2025 KHO ĐỀ AZOTA. All rights reserved.</div>

    <script>
        let serverReady = false;

        fetch("/ping-vietnamnet")
            .then(res => res.json())
            .then(data => {
                const status = document.getElementById("serverStatus");
                if (data.ok) {
                    serverReady = true;
                    status.innerHTML = "✅ Máy chủ sẵn sàng.";
                    status.style.color = "lightgreen";
                } else {
                    serverReady = false;
                    status.innerHTML = "🚫 Không thể kết nối máy chủ.";
                    status.style.color = "red";
                }
            })
            .catch(() => {
                const status = document.getElementById("serverStatus");
                serverReady = false;
                status.innerHTML = "⚠️ Không thể kiểm tra máy chủ.";
                status.style.color = "orange";
            });

        document.getElementById("formTraCuu").addEventListener("submit", function(e) {
            e.preventDefault();
            const ketQuaDiv = document.getElementById("ketQua");
            const sbd = document.getElementById("sbd").value.trim();

            if (!serverReady) {
                ketQuaDiv.innerHTML = "❌ Máy chủ chưa sẵn sàng. Vui lòng thử lại sau.";
                return;
            }

            if (!sbd) {
                ketQuaDiv.innerHTML = "⚠️ Vui lòng nhập số báo danh.";
                return;
            }

            ketQuaDiv.innerHTML = "🔍 Đang tra cứu...";
            fetch(`/tra-cuu?sbd=${encodeURIComponent(sbd)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        ketQuaDiv.innerHTML = data.result;
                    } else {
                        ketQuaDiv.innerHTML = "<p style='color: red;'>❌ Không tìm thấy kết quả.</p>";
                    }
                })
                .catch(err => {
                    ketQuaDiv.innerHTML = "<p style='color: red;'>❗ Có lỗi xảy ra. Vui lòng thử lại.</p>";
                });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/tra-cuu")
def tra_cuu():
    sbd = request.args.get("sbd", "")
    result = Crawl_THPTQG(sbd)
    if result:
        return jsonify({"success": True, "result": result})
    return jsonify({"success": False})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
