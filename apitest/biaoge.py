from flask import Flask, render_template_string
import pandas as pd

app = Flask(__name__)

@app.route('/biaoge')
def index():
    # 读取 Excel 文件
    df = pd.read_excel('秋招信息表.xlsx')

    # 将 DataFrame 转换为 HTML 表格
    html_table = df.to_html(classes='table table-striped', index=False)

    # 使用简单的 HTML 模板展示表格
    html_template = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <title>Excel Viewer</title>
      </head>
      <body>
        <div class="container">
          <h1 class="mt-5">Excel File Viewer</h1>
          {html_table}
        </div>
      </body>
    </html>
    """
    return render_template_string(html_template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
