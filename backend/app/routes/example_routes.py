from flask import Blueprint, jsonify

example_bp = Blueprint("example", __name__)


@example_bp.route('/', methods=['GET'])
def example():
    return jsonify({"message": "Hello World"})


__all__ = [example_bp]
