from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os

# 1. 初始化 FastAPI 应用
app = FastAPI(
    title="Employee Burnout Prediction API",
    description="SWE402 Data Mining Assignment - Model Deployment Layer",
    version="1.0.0"
)

# 2. 动态加载训练好的冠军模型管道 (包含 StandardScaler 和 RandomForest)
MODEL_PATH = "best_burnout_model.pkl"

if not os.path.exists(MODEL_PATH):
    # 兼容本地开发和云端部署的路径容错处理
    raise RuntimeError(f"Critical Error: Model file '{MODEL_PATH}' not found!")

# 加载模型管道
model_pipeline = joblib.load(MODEL_PATH)


# 3. 定义前端/n8n 传过来的数据结构 (严格对齐训练集除了 Burn Rate 外的 6 个特征)
class EmployeeData(BaseModel):
    Gender: int                 # 0: Female, 1: Male
    Company_Type: int           # 0: Service, 1: Product
    WFH_Setup_Available: int    # 0: No, 1: Yes
    Designation: float          # 0.0 - 5.0 (职位等级)
    Resource_Allocation: float  # 1.0 - 10.0 (工作资源/工作量)
    Mental_Fatigue_Score: float # 0.0 - 10.0 (心理疲劳指数)


# 4. 健康检查接口 (用于云端平台心跳检测，确保部署不挂掉)
@app.get("/")
def home():
    return {
        "status": "healthy",
        "message": "Employee Burnout Prediction API is up and running!",
        "course_code": "SWE402",
        "assignment": "Agentic AI Workflow Integration"
    }


# 5. 核心预测接口：供 n8n Workflow 远程调用
@app.post("/predict")
def predict_burnout(data: EmployeeData):
    try:
        # 将接收到的 JSON 数据转换为 Pandas DataFrame (特征名称和顺序必须与训练时完全一致)
        input_df = pd.DataFrame([{
            'Gender': data.Gender,
            'Company Type': data.Company_Type,  # 注意：DataFrame 中的列名要带有空格，与训练集严格一致
            'WFH Setup Available': data.WFH_Setup_Available,
            'Designation': data.Designation,
            'Resource Allocation': data.Resource_Allocation,
            'Mental Fatigue Score': data.Mental_Fatigue_Score
        }])
        
        # 使用 Pipeline 进行一键预测 (内部会自动调用之前训练好的 StandardScaler 进行缩放)
        prediction = model_pipeline.predict(input_df)[0]
        
        # 边界控制：Burn Rate 理论上在 0.0 到 1.0 之间
        burn_rate = float(np.clip(prediction, 0.0, 1.0))
        
        # 返回标准的 JSON 响应供接下来的 n8n AI Agent 读取和推理
        return {
            "prediction_status": "success",
            "burn_rate": round(burn_rate, 4),
            "burn_rate_percentage": f"{round(burn_rate * 100, 2)}%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction internal error: {str(e)}")