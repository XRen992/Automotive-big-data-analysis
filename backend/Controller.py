from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from your_service_module import *  # 导入Service层提供的功能

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


# 辅助函数：检查文件扩展名
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/v1/upload/excel', methods=['POST'])
def upload_excel():
    """处理Excel文件上传"""
    if 'excelFile' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['excelFile']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 调用Service层处理
        result = ExcelService.process_excel(file_path)

        # 返回处理结果
        return jsonify({
            'status': 'success',
            'processed_rows': result['processed'],
            'errors': result.get('errors', [])
        }), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/v1/market/overview', methods=['GET'])
def get_market_overview():
    """获取市场概览数据"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    # 调用Service层
    overview_data = MarketService.get_market_overview(year, month)
    return jsonify(overview_data), 200


@app.route('/api/v1/market/trends', methods=['GET'])
def get_market_trends():
    """获取市场趋势数据"""
    metric = request.args.get('metric', 'registrations')
    granularity = request.args.get('granularity', 'monthly')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # 验证必需参数
    if not all([metric, granularity, start_date, end_date]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # 调用Service层
    trends_data = MarketService.get_market_trends(
        metric, granularity, start_date, end_date
    )
    return jsonify(trends_data), 200


@app.route('/api/v1/market/price_distribution', methods=['GET'])
def get_price_distribution():
    """获取价格区间分布"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    # 调用Service层
    distribution = MarketService.get_price_distribution(year, month)
    return jsonify(distribution), 200


@app.route('/api/v1/brands', methods=['GET'])
def get_brands():
    """获取所有品牌列表"""
    brands = BrandService.get_all_brands()
    return jsonify([brand.to_dict() for brand in brands]), 200


@app.route('/api/v1/brands/<brand_name>/models', methods=['GET'])
def get_brand_models(brand_name):
    """获取特定品牌下的车型"""
    models = ModelService.get_models_by_brand(brand_name)
    return jsonify([model.name for model in models]), 200


@app.route('/api/v1/models/<model_id>', methods=['GET'])
def get_model_details(model_id):
    """获取车型详细信息"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    granularity = request.args.get('granularity', 'monthly')

    # 调用Service层
    model_data = ModelService.get_model_details(
        model_id, start_date, end_date, granularity
    )
    return jsonify(model_data), 200


@app.route('/api/v1/models', methods=['GET'])
def search_models():
    """车型多条件筛选"""
    # 获取所有可能的查询参数
    params = {
        'brand': request.args.get('brand'),
        'type': request.args.get('type'),
        'min_price': request.args.get('min_price', type=float),
        'max_price': request.args.get('max_price', type=float),
        'min_hp': request.args.get('min_hp', type=int),
        'sort_by': request.args.get('sort_by', 'popularity'),
        'order': request.args.get('order', 'desc'),
        'page': request.args.get('page', 1, type=int),
        'limit': request.args.get('limit', 20, type=int)
    }

    # 调用Service层
    models = ModelService.search_models(params)
    return jsonify({
        'page': params['page'],
        'limit': params['limit'],
        'results': [model.to_dict() for model in models]
    }), 200


@app.route('/api/v1/cities', methods=['GET'])
def get_cities():
    """获取所有城市列表"""
    cities = RegionService.get_all_cities()
    return jsonify([city.name for city in cities]), 200


@app.route('/api/v1/cities/rankings', methods=['GET'])
def get_city_rankings():
    """获取城市排名"""
    metric = request.args.get('metric', 'registrations')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    rankings = RegionService.get_city_rankings(metric, year, month)
    return jsonify(rankings), 200


@app.route('/api/v1/consumer_insights/preferences', methods=['GET'])
def get_consumer_preferences():
    """获取消费者偏好"""
    dimension = request.args.get('dimension', 'type')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)

    preferences = ConsumerService.get_preferences(dimension, year, month)
    return jsonify(preferences), 200


@app.route('/api/v1/recommendations', methods=['GET'])
def get_recommendations():
    """获取个性化推荐"""
    user_id = request.args.get('user_id')
    preferred_type = request.args.get('preferred_type')
    preferred_price_range = request.args.get('preferred_price_range')

    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    # 调用推荐服务
    recommendations = RecommendationService.get_recommendations(
        user_id,
        preferred_type,
        preferred_price_range
    )
    return jsonify([rec.to_dict() for rec in recommendations]), 200


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
