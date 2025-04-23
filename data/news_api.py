import flask
from flask import jsonify, make_response, Flask, request
from flask_restful import reqparse, abort, Api, Resource
from . import db_session
from .work import Work

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)
app = Flask(__name__)
api = Api(app)

def abort_if_news_not_found(news_id):
    session = db_session.create_session()
    work = session.query(Work).get(news_id)
    if not work:
        abort(404, message=f"News {news_id} not found")

class NewsResource(Resource):
    def get(self, work_id):
        abort_if_news_not_found(work_id)
        session = db_session.create_session()
        work = session.query(Work).get(work_id)
        return jsonify({'work': work.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        work = session.query(Work).get(news_id)
        session.delete(work)
        session.commit()
        return jsonify({'success': 'OK'})

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)

class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        work = session.query(Work).all()
        return jsonify({'work': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in work]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        work = Work(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(work)
        session.commit()
        return jsonify({'id': work.id})
# @blueprint.route('/api/news')
# def get_news():
#     db_sess = db_session.create_session()
#     work = db_sess.query(Work).all()
#     return jsonify(
#         {
#             'news':
#                 [item.to_dict(only=('title', 'content', 'user.name'))
#                  for item in work]
#         }
#     )
@blueprint.route('/api/jobs')
def get_news():
    db_sess = db_session.create_session()
    work = db_sess.query(Work).all()
    return jsonify(
        {
            'work':

                [item.to_dict(only=('title', 'content'))
                 for item in work]

        }
    )
    return "Обработчик в news_api"


@blueprint.route('/api/jobs/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    work = db_sess.query(Work).get(news_id)
    if not work:
        return make_response(jsonify({'error': 'Not found'}), 404)
    return jsonify(
        {
            'news': work.to_dict(only=(
                'id', 'title', 'content', 'colab', 'created_date', 'user_id', 'is_private'))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def add_jobs():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['title', 'content', 'experience', 'colab', 'user_id', 'is_private']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    work = Work(
        title=request.json['title'],
        content=request.json['content'],
        experience=request.json['experience'],
        colab=request.json['colab'],
        user_id=request.json['user_id'],
        is_private=request.json['is_private']
    )
    db_sess.add(work)
    db_sess.commit()
    return jsonify({'id': work.id})


@blueprint.route('/api/delete_jobs/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    db_sess = db_session.create_session()
    work = db_sess.query(Work).get(news_id)
    if not work:
        return make_response(jsonify({'error': 'Not found'}), 404)
    db_sess.delete(work)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/redact_jobs/<int:news_id>', methods=['PUT'])
def redact_news(news_id):
    db_sess = db_session.create_session()
    work = db_sess.query(Work).get(news_id)
    if not work:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['title', 'content', 'experience', 'colab', 'user_id', 'is_private']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess.delete(work)
    db_sess.commit()
    return jsonify({'success': 'OK'})



