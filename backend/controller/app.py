from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 模拟数据库
cars_db = []
cities_db = []
market_trends_data = []  # 重命名以避免冲突
preferences_db = []

'''
# 初始化模拟数据
def init_sample_data():
    global cars_db, cities_db, market_trends_data, preferences_db

    # 品牌和车型数据
    brands = ['丰田', '本田', '宝马', '特斯拉', '比亚迪']
    car_types = ['SUV', '轿车', 'MPV', '跑车', '新能源']

    for brand_id, brand in enumerate(brands):
        for model_id in range(1, 4):
            car = {
                'id': str(uuid.uuid4()),  # 添加唯一ID
                'brand_id': brand_id,
                'brand': brand,
                'model_id': f"{brand_id}-{model_id}",
                'model': f"{brand}车型{model_id}",
                'guide_price': 150000 + model_id * 50000,
                'horsepower': 150 + model_id * 30,
                'doors': 4 if model_id % 2 == 0 else 2,
                'min_price': 120000 + model_id * 40000,
                'car_type': car_types[model_id % len(car_types)],
                'fuel_consumption': 6.5 + model_id * 0.5,
                'attention': 5000 + model_id * 2000,
                'discount': 0.1 if model_id == 1 else 0.15,
                'history_prices': [
                    {'date': '2023-01', 'price': 160000},
                    {'date': '2023-06', 'price': 155000},
                    {'date': '2024-01', 'price': 150000}
                ]
            }
            cars_db.append(car)

    # 城市数据
    cities = ['北京', '上海', '广州', '深圳', '成都', '杭州']
    for city_id, city in enumerate(cities):
        cities_db.append({
            'id': city_id,
            'city': city,
            'registrations': 50000 + city_id * 10000
        })

    # 市场趋势数据
    for month in range(1, 13):
        market_trends_data.append({
            'date': f'2023-{month:02d}',
            'registrations': 200000 + month * 5000,
            'attention': 1000000 + month * 20000,
            'avg_price': 250000 + month * 1000
        })

    # 消费者偏好数据
    preferences_db = [
        {'type': 'SUV', 'preference': 0.35},
        {'type': '轿车', 'preference': 0.3},
        {'type': '新能源', 'preference': 0.25},
        {'type': 'MPV', 'preference': 0.08},
        {'type': '跑车', 'preference': 0.02}
    ]
'''
@app.route('/')
def index():
    return render_template('index.html')

# 数据上传API
@app.route('/api/v1/upload/excel', methods=['POST'])
def upload_excel():
    if 'excelFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['excelFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # 保存文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        # 解析Excel
        df = pd.read_excel(filename)
        processed_count = len(df)

        # 实际应用中这里会有数据库插入逻辑
        return jsonify({
            'status': 'success',
            'message': f'Processed {processed_count} rows'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 品牌与车型深度分析API
@app.route('/api/v1/brands', methods=['GET'])
def get_brands():
    brands = list(set(car['brand'] for car in cars_db))
    return jsonify({'brands': brands}), 200


@app.route('/api/v1/brands/<brand_name>/models', methods=['GET'])
def get_brand_models(brand_name):
    models = [{'id': car['model_id'], 'name': car['model']}
              for car in cars_db if car['brand'] == brand_name]
    return jsonify({'models': models}), 200


@app.route('/api/v1/models/<model_id>', methods=['GET'])
def get_model_details(model_id):
    car = next((car for car in cars_db if car['model_id'] == model_id), None)
    if not car:
        return jsonify({'error': 'Model not found'}), 404

    # 复制对象并删除不需要的字段
    details = car.copy()
    details.pop('id', None)
    details.pop('brand_id', None)
    return jsonify(details), 200


# 区域市场分析API
@app.route('/api/v1/cities', methods=['GET'])
def get_cities():
    cities = [{'id': city['id'], 'name': city['city']} for city in cities_db]
    return jsonify({'cities': cities}), 200


@app.route('/api/v1/cities/rankings', methods=['GET'])
def get_city_rankings():
    metric = request.args.get('metric', 'registrations')
    # 确保请求的指标有效
    if metric not in ['registrations', 'attention']:
        return jsonify({'error': 'Invalid metric'}), 400

    sorted_cities = sorted(cities_db, key=lambda x: x.get(metric, 0), reverse=True)
    # 简化输出
    result = [{'city': city['city'], metric: city.get(metric, 0)} for city in sorted_cities]
    return jsonify({'rankings': result}), 200


# 消费者建议API
@app.route('/api/v1/recommendations', methods=['GET'])
def get_recommendations():
    # 获取筛选条件
    filters = {
        'brand': request.args.get('brand'),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'min_hp': request.args.get('min_hp', type=int),
        'doors': request.args.get('doors', type=int),
        'car_type': request.args.get('car_type'),
    }

    # 应用筛选条件
    filtered_cars = cars_db.copy()

    if filters['brand']:
        filtered_cars = [car for car in filtered_cars if car['brand'] == filters['brand']]

    if filters['min_price'] is not None:
        filtered_cars = [car for car in filtered_cars if car['min_price'] >= filters['min_price']]

    if filters['max_price'] is not None:
        filtered_cars = [car for car in filtered_cars if car['min_price'] <= filters['max_price']]

    if filters['min_hp'] is not None:
        filtered_cars = [car for car in filtered_cars if car['horsepower'] >= filters['min_hp']]

    if filters['doors'] is not None:
        filtered_cars = [car for car in filtered_cars if car['doors'] == filters['doors']]

    if filters['car_type']:
        filtered_cars = [car for car in filtered_cars if car['car_type'] == filters['car_type']]

    # 按关注度排序
    filtered_cars.sort(key=lambda x: x['attention'], reverse=True)

    # 简化输出
    recommendations = [{
        'id': car['model_id'],
        'brand': car['brand'],
        'model': car['model'],
        'min_price': car['min_price'],
        'horsepower': car['horsepower'],
        'car_type': car['car_type'],
        'attention': car['attention']
    } for car in filtered_cars]

    return jsonify({'recommendations': recommendations}), 200


# 市场分析API
@app.route('/api/v1/market/overview', methods=['GET'])
def market_overview():
    total_registrations = sum(city['registrations'] for city in cities_db)
    avg_attention = sum(car['attention'] for car in cars_db) / len(cars_db) if cars_db else 0

    # 按品牌统计
    from collections import defaultdict
    brand_counts = defaultdict(int)
    for car in cars_db:
        brand_counts[car['brand']] += 1

    # 找到关注度最高的车型
    if cars_db:
        top_car = max(cars_db, key=lambda x: x['attention'])
        top_car_info = f"{top_car['brand']} {top_car['model']} (关注度: {top_car['attention']})"
    else:
        top_car_info = "无数据"

    return jsonify({
        'total_registrations': total_registrations,
        'avg_attention': avg_attention,
        'popular_brands': dict(brand_counts),
        'top_car': top_car_info
    }), 200


@app.route('/api/v1/market/trends', methods=['GET'])
def market_trends():
    metric = request.args.get('metric', 'registrations')
    # 确保请求的指标有效
    if metric not in ['registrations', 'attention', 'avg_price']:
        return jsonify({'error': 'Invalid metric'}), 400

    granularity = request.args.get('granularity', 'monthly')

    # 实际应用中这里会有更复杂的时间过滤逻辑
    # 使用重命名后的变量
    data_points = [{'date': point['date'], 'value': point[metric]} for point in market_trends_data]

    return jsonify({
        'metric': metric,
        'granularity': granularity,
        'data': data_points
    }), 200


@app.route('/api/v1/market/price_distribution', methods=['GET'])
def price_distribution():
    # 定义价格区间
    price_ranges = [
        (0, 100000),
        (100000, 200000),
        (200000, 300000),
        (300000, 500000),
        (500000, float('inf'))
    ]

    distribution = []
    for min_price, max_price in price_ranges:
        cars_in_range = [car for car in cars_db if min_price <= car['min_price'] < max_price]
        count = len(cars_in_range)
        avg_attention = sum(car['attention'] for car in cars_in_range) / count if count > 0 else 0

        distribution.append({
            'range': f"{min_price // 1000}万-{max_price // 1000}万",
            'count': count,
            'avg_attention': avg_attention
        })

    return jsonify({'distribution': distribution}), 200


# 消费者洞察API
@app.route('/api/v1/consumer_insights/preferences', methods=['GET'])
def consumer_preferences():
    dimension = request.args.get('dimension', 'type')

    if dimension == 'type':
        return jsonify(preferences_db), 200
    else:
        # 其他维度的模拟数据
        return jsonify([{
            'range': '100-150马力',
            'preference': 0.4
        }, {
            'range': '150-200马力',
            'preference': 0.35
        }, {
            'range': '200+马力',
            'preference': 0.25
        }]), 200

'''
@app.route('/')
def home():
    return """
    <h1>汽车大数据分析平台</h1>
    <p>欢迎使用汽车大数据分析平台API服务</p>
    <p>可用API端点:</p>
    <ul>
        <li>/api/v1/brands - 获取所有品牌</li>
        <li>/api/v1/brands/&lt;brand_name&gt;/models - 获取品牌车型</li>
        <li>/api/v1/models/&lt;model_id&gt; - 获取车型详情</li>
        <li>/api/v1/cities - 获取城市列表</li>
        <li>/api/v1/cities/rankings - 获取城市上牌量排名</li>
        <li>/api/v1/recommendations - 车型推荐</li>
        <li>/api/v1/market/overview - 市场概览</li>
        <li>/api/v1/market/trends - 市场趋势</li>
        <li>/api/v1/upload/excel - 上传Excel数据(POST)</li>
    </ul>
    """
'''

if __name__ == '__main__':
    init_sample_data()
    app.run(debug=True, port=5000)
