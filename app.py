from flask import Flask, request, render_template, jsonify, g
import replicate
import os
import time
import google.generativeai  

# 设置环境变量来安全地处理密钥
os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")
google_api_key = os.getenv("GOOGLE_API_KEY")

# 使用环境变量中的密钥初始化Google Generative AI模型
google.generativeai.configure(api_key=google_api_key)
app = Flask(__name__)

# 全局变量
r = ""
first_time = 1
image_prompt = ""

# 路由定义
@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/main", methods=["GET", "POST"])
def main():
    global r, first_time
    if first_time == 1:
        r = request.form.get("r")
        first_time = 0
    return render_template("main.html", r=r)

@app.route("/text_gpt", methods=["GET", "POST"])
def text_gpt():
    return render_template("text_gpt.html")

@app.route("/text_result", methods=["GET", "POST"])
def text_result():
    global first_time
    q = request.form.get("q")
    try:
        # 检查请求之间的间隔时间，确保不超过 API 速率限制
        last_request_time = getattr(g, 'last_request_time', None)
        if last_request_time:
            elapsed = time.time() - last_request_time
            if elapsed < 2:  # 确保至少有2秒间隔
                time.sleep(2 - elapsed)
        response = google.generativeai.generate_text(
            model="gemini-1",  # 假设这是正确的模型ID
            messages=[{"role": "user", "content": q}]
        )
        g.last_request_time = time.time()
        return render_template("text_result.html", r=response.choices[0].message.content)
    except google.generativeai.error.GoogleGenerativeAIError as e:  # 假设这是错误类
        return jsonify({"error": str(e)}), 429

@app.route("/image_gpt", methods=["GET", "POST"])
def image_gpt():
    return render_template("image_gpt.html")

@app.route("/image_result", methods=["GET", "POST"])
def image_result():
    global image_prompt
    q = request.form.get("q")
    response = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={"prompt": q}
    )
    image_prompt = q
    return render_template("image_result.html", r=response[0])

@app.route("/recreate", methods=["GET", "POST"])
def recreate():
    global image_prompt
    response = replicate.run(
        "stability-ai/stable-diffusion:db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf",
        input={"prompt": image_prompt}
    )
    return render_template("recreate.html", r=response[0])

@app.route("/NTU", methods=["GET", "POST"])
def NTU():
    return render_template("NTU.html")

@app.route("/more_NTU", methods=["GET", "POST"])
def more_NTU():
    return render_template("more_NTU.html")

@app.route("/end", methods=["GET", "POST"])
def end():
    global first_time, r
    first_time = 1
    return render_template("end.html", r=r)

if __name__ == "__main__":
    app.run()
